#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import select
import csv
from datetime import datetime
from evdev import InputDevice, ecodes, list_devices, AbsInfo

# Import the Waveshare SDK
sys.path.append("..")
from scservo_sdk import *

# -------------------------------------------------
# HARDWARE SETTINGS
# -------------------------------------------------
DEVICENAME  = '/dev/ttyACM1'    # Check your port (ttyACM0 or ttyACM1)
BAUDRATE    = 1000000

ID_LEFT     = 1                 # Left Gripper Servo
ID_RIGHT    = 2                 # Right Gripper Servo

# -------------------------------------------------
# DRIVE & LIMIT SETTINGS
# -------------------------------------------------
MAX_SPEED   = 2400
ACCEL       = 50
DEADZONE    = 0.15
LEVEL       = 2
DEBOUNCE_MS = 250

# --- HOMING SETTINGS ---
HOMING_SPEED          = 800     # Slower speed for gentle collision with hard stops
HOMING_LOAD_THRESHOLD = 280     # ST3215 load value indicating a hard stop (Tune this! 0-1000 range)
OFFSET_DEGREES        = 3.0     # Degrees to back away from the absolute hard stop
OFFSET_STEPS          = int((OFFSET_DEGREES / 360.0) * 4096)  # Convert degrees to steps (~34 steps)

# Dictionary to store our safe operational limits
servo_limits = {
    ID_LEFT:  {'min': 0, 'max': 4095},
    ID_RIGHT: {'min': 0, 'max': 4095}
}

is_homed = False

# -------------------------------------------------
# GAMEPAD DEFINITIONS
# -------------------------------------------------
AX_LEFT_X  = ecodes.ABS_X
AX_RIGHT_X = ecodes.ABS_RX
AX_RIGHT_Z = ecodes.ABS_Z

BTN_SQUARE   = ecodes.BTN_WEST
BTN_CROSS    = ecodes.BTN_SOUTH
BTN_TRIANGLE = ecodes.BTN_NORTH
BTN_L1       = ecodes.BTN_TL
BTN_R1       = ecodes.BTN_TR
BTN_SELECT   = ecodes.BTN_SELECT  # Used to trigger manual homing

JOY = None
JOY_STATE = {'axes': {}, 'btn': set()}
PREV_BTN = set()
last_toggle = {'quit': 0, 'r1': 0, 'l1': 0, 'mode': 0, 'home': 0}

# -------------------------------------------------
# TELEMETRY LOGGER SETUP
# -------------------------------------------------
LOG_FILE = f"datas/servo_telemetry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
def init_logger():
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "ID", "Position", "Speed", "Load", "Voltage", "Temperature", "Current"])

def log_telemetry(packetHandler, servo_id):
    """Reads all feedback from the servo and writes to CSV."""
    pos, res_p, err = packetHandler.ReadPos(servo_id)
    spd, res_s, err = packetHandler.ReadSpeed(servo_id)
    load, res_l, err = packetHandler.ReadLoad(servo_id)
    volt, res_v, err = packetHandler.ReadVoltage(servo_id)
    temp, res_t, err = packetHandler.ReadTemper(servo_id)
    curr, res_c, err = packetHandler.ReadCurrent(servo_id)

    # Ensure all reads were successful before logging
    if res_p == COMM_SUCCESS and res_l == COMM_SUCCESS:
        # Load value is often signed (direction + magnitude), so we grab absolute magnitude
        load_mag = abs(load) 
        
        with open(LOG_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([time.time(), servo_id, pos, spd, load_mag, volt, temp])
        
        return pos, spd, load_mag
    return None, None, None

# -------------------------------------------------
# SENSORLESS HOMING LOGIC
# -------------------------------------------------
def execute_homing(packetHandler):
    global is_homed, servo_limits
    print("\n\n[WARNING] Starting Sensorless Homing Sequence...")
    print("Keep hands clear! Servos will seek hard stops.")
    
    for servo_id in [ID_LEFT, ID_RIGHT]:
        print(f"\n--- Homing Servo ID {servo_id} ---")
        limits = []
        
        # Drive in both directions (+1 CW, -1 CCW)
        for direction in [1, -1]:
            dir_str = "CW" if direction == 1 else "CCW"
            print(f"Seeking {dir_str} limit...")
            
            # Start moving slowly
            packetHandler.WriteSpec(servo_id, HOMING_SPEED * direction, ACCEL)
            time.sleep(0.3) # Wait for initial starting inertia to settle
            
            spike_count = 0
            while True:
                pos, spd, load = log_telemetry(packetHandler, servo_id)
                
                if load is not None:
                    if load > HOMING_LOAD_THRESHOLD:
                        spike_count += 1
                    else:
                        spike_count = 0
                        
                    # Require 3 consecutive high-load readings to confirm a hard stop
                    # (Prevents false positives from random noise)
                    if spike_count >= 3:
                        packetHandler.WriteSpec(servo_id, 0, ACCEL) # EMERGENCY STOP
                        print(f"> Hard stop detected at position: {pos} (Load: {load})")
                        limits.append(pos)
                        time.sleep(0.5) # Let mechanical tension release
                        break
                
                time.sleep(0.01)
                
        # Calculate safe operational bounds
        raw_min = min(limits)
        raw_max = max(limits)
        
        # Apply the offset to stay slightly away from the physical wall
        safe_min = raw_min + OFFSET_STEPS
        safe_max = raw_max - OFFSET_STEPS
        
        servo_limits[servo_id]['min'] = safe_min
        servo_limits[servo_id]['max'] = safe_max
        
        print(f"Calibration Complete ID {servo_id}: Safe Range = [{safe_min} to {safe_max}]")

    is_homed = True
    print("\n[SUCCESS] Homing Complete. Returning to manual control.")

# -------------------------------------------------
# JOYSTICK LOGIC
# -------------------------------------------------
def find_joystick():
    for p in list_devices():
        d = InputDevice(p)
        name = (d.name or "").lower()
        if any(k in name for k in ["logitech", "gamepad", "joystick", "controller", "xbox", "dualshock"]):
            return d
    return None

def norm_axis(dev, code, val):
    info = dev.absinfo(code) if hasattr(dev, "absinfo") else None
    if isinstance(info, AbsInfo) and info.max != info.min:
        x = (val - (info.min + info.max) / 2) / ((info.max - info.min) / 2)
    else:
        x = (val - 32767) / 32767.0
    if abs(x) < DEADZONE: x = 0.0
    return max(-1.0, min(1.0, x))

def poll_joystick(timeout=0.0):
    if not JOY: return
    r, _, _ = select.select([JOY.fd], [], [], timeout)
    if not r: return
    for ev in JOY.read():
        if ev.type == ecodes.EV_ABS and ev.code in (AX_LEFT_X, AX_RIGHT_X, AX_RIGHT_Z):
            JOY_STATE['axes'][ev.code] = norm_axis(JOY, ev.code, ev.value)
        elif ev.type == ecodes.EV_KEY:
            if ev.value == 1: JOY_STATE['btn'].add(ev.code)
            elif ev.value == 0: JOY_STATE['btn'].discard(ev.code)

def button_just_pressed(code, now_ms, name):
    if (code in JOY_STATE['btn']) and (code not in PREV_BTN) and (now_ms - last_toggle[name] > DEBOUNCE_MS):
        last_toggle[name] = now_ms
        return True
    return False

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
def main():
    global JOY, LEVEL, PREV_BTN, is_homed
    single_stick_mode = False

    portHandler = PortHandler(DEVICENAME)
    packetHandler = sms_sts(portHandler)
        
    if not portHandler.openPort():
        print("Failed to open the port")
        quit()
    if not portHandler.setBaudRate(BAUDRATE):
        print("Failed to change the baudrate")
        quit()

    packetHandler.WheelMode(ID_LEFT)
    packetHandler.WheelMode(ID_RIGHT)
    init_logger()

    JOY = find_joystick()
    if JOY:
        print(f"[JOY] Connected: {JOY.name}")
        try: JOY.grab()
        except: pass
    else:
        print("[ERROR] No gamepad found. Exiting.")
        portHandler.closePort()
        return

    # --- AUTO-HOME ON STARTUP ---
    execute_homing(packetHandler)

    print(f"""
    ---------------------------------------------------------
      Logitech Gripper Control Active (Logging to {LOG_FILE})
    ---------------------------------------------------------
      [Select/Back]     -> Trigger Manual Re-Homing
      [Triangle/Y]      -> Toggle 1-Stick vs 2-Stick Mode
      [Square/X]        -> Quit
      [Cross/A]         -> Emergency Brake
    ---------------------------------------------------------
    """)

    try:
        while True:
            now_ms = time.time() * 1000.0
            poll_joystick(0.0)

            # --- Read current positions & Log Telemetry ---
            pos_L, _, _ = log_telemetry(packetHandler, ID_LEFT)
            pos_R, _, _ = log_telemetry(packetHandler, ID_RIGHT)
            
            if pos_L is None or pos_R is None:
                continue # Skip loop if telemetry read failed

            # --- Check Buttons ---
            if button_just_pressed(BTN_SELECT, now_ms, 'home'):
                execute_homing(packetHandler)
                continue
                
            if button_just_pressed(BTN_TRIANGLE, now_ms, 'mode'):
                single_stick_mode = not single_stick_mode
                mode_str = "SINGLE-STICK" if single_stick_mode else "DUAL-STICK"
                print(f"\n[MODE] Switched to {mode_str}")

            if button_just_pressed(BTN_SQUARE, now_ms, 'quit'):
                break

            # --- Calculate Speeds ---
            current_max = int(MAX_SPEED * (LEVEL / 4.0))

            if BTN_CROSS in JOY_STATE['btn']:
                speed_L, speed_R = 0, 0
            else:
                left_x = JOY_STATE['axes'].get(AX_LEFT_X, 0.0)
                
                if single_stick_mode:
                    speed_L = int(left_x * current_max)
                    speed_R = int(-left_x * current_max)
                else:
                    right_x = JOY_STATE['axes'].get(AX_RIGHT_X, 0.0)
                    if abs(JOY_STATE['axes'].get(AX_RIGHT_Z, 0.0)) > abs(right_x):
                        right_x = JOY_STATE['axes'].get(AX_RIGHT_Z, 0.0)
                    speed_L = int(left_x * current_max)
                    speed_R = int(right_x * current_max)

            # --- SOFTWARE LIMIT ENFORCEMENT ---
            # If position is outside safe bounds, only allow speeds that move it back inside.
            # Assuming Positive speed (+) INCREASES position, Negative speed (-) DECREASES position.
            
            if pos_L >= servo_limits[ID_LEFT]['max'] and speed_L > 0: speed_L = 0
            if pos_L <= servo_limits[ID_LEFT]['min'] and speed_L < 0: speed_L = 0
            
            if pos_R >= servo_limits[ID_RIGHT]['max'] and speed_R > 0: speed_R = 0
            if pos_R <= servo_limits[ID_RIGHT]['min'] and speed_R < 0: speed_R = 0

            # --- Write to Servos ---
            packetHandler.WriteSpec(ID_LEFT, speed_L, ACCEL)
            packetHandler.WriteSpec(ID_RIGHT, speed_R, ACCEL)
            
            PREV_BTN = set(JOY_STATE['btn'])
            time.sleep(0.01) # 100Hz loop

    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down safely. Stopping motors...")
        packetHandler.WriteSpec(ID_LEFT, 0, ACCEL)
        packetHandler.WriteSpec(ID_RIGHT, 0, ACCEL)
        portHandler.closePort()
        if JOY: 
            try: JOY.ungrab()
            except: pass

if __name__ == "__main__":
    main()