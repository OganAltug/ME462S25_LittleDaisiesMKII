#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, time, select
import serial
from evdev import InputDevice, ecodes, list_devices, AbsInfo

# -------------------------------------------------
# HARDWARE SETTINGS
# -------------------------------------------------
PORT       = "/dev/ttyACM0"      # Waveshare ST3215 Driver Board
BAUD       = 1000000

LEFT_ID, RIGHT_ID   = 1, 2
DIR_LEFT, DIR_RIGHT = 1, 1       # Invert (-1) if a motor spins backwards physically
MAXV                = 3400       # ST3215 Max Speed

# -------------------------------------------------
# DRIVE SETTINGS
# -------------------------------------------------
LEVEL       = 3         # Speed multiplier (1 to 4)
DEBOUNCE_MS = 250
DEAD        = 0.15      # Joystick deadzone

# -------------------------------------------------
# GAMEPAD DEFINITIONS
# -------------------------------------------------
AX_LEFT_Y  = ecodes.ABS_Y
AX_LEFT_X  = ecodes.ABS_X
AX_RIGHT_X = ecodes.ABS_RX
AX_RIGHT_Z = ecodes.ABS_Z   # Right stick X often maps here on Logitech

BTN_SQUARE = ecodes.BTN_WEST
BTN_CROSS  = ecodes.BTN_SOUTH
BTN_L1     = ecodes.BTN_TL
BTN_R1     = ecodes.BTN_TR

JOY = None
JOY_STATE = {'axes': {}, 'btn': set()}
PREV_BTN = set()
last_toggle = {'quit': 0, 'r1': 0, 'l1': 0}

# -------------------------------------------------
# ST3215 MOTOR CONTROLLER
# -------------------------------------------------
class ST3215Controller:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=0.01)

    def write_register_byte(self, servo_id, address, value):
        header = [0xFF, 0xFF]
        length = 0x04
        instruction = 0x03
        checksum = (~(servo_id + length + instruction + address + value)) & 0xFF
        packet = header + [servo_id, length, instruction, address, value, checksum]
        self.ser.write(bytearray(packet))
        time.sleep(0.005)
        self.ser.read_all()

    def set_operating_mode(self, servo_id, mode):
        # 0 = Servo (Angle), 1 = Motor (Continuous)
        self.write_register_byte(servo_id, 0x21, mode)

    def sync_write_velocity(self, vL, vR):
        """Broadcasts a synchronized speed command to both wheels."""
        # Apply physical mounting direction
        vL_real = int(vL * DIR_LEFT)
        vR_real = int(vR * DIR_RIGHT)

        def format_speed(v):
            spd = max(0, min(MAXV, abs(v)))
            if v < 0:
                spd |= 0x8000 # Set highest bit for reverse rotation
            return spd & 0xFF, (spd >> 8) & 0xFF

        spdL_L, spdL_H = format_speed(vL_real)
        spdR_L, spdR_H = format_speed(vR_real)

        header = [0xFF, 0xFF]
        broadcast_id = 0xFE
        instruction = 0x83
        address = 0x2E        # Goal Speed Register
        data_length = 0x02

        packet_length = (data_length + 1) * 2 + 4
        params = [LEFT_ID, spdL_L, spdL_H, RIGHT_ID, spdR_L, spdR_H]

        checksum_sum = broadcast_id + packet_length + instruction + address + data_length + sum(params)
        checksum = (~checksum_sum) & 0xFF

        packet = header + [broadcast_id, packet_length, instruction, address, data_length] + params + [checksum]

        self.ser.write(bytearray(packet))
        self.ser.read_all()

    def stop(self):
        self.sync_write_velocity(0, 0)

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

    if abs(x) < DEAD:
        x = 0.0
    return max(-1.0, min(1.0, x))

def poll_joystick(timeout=0.0):
    if not JOY: return
    r, _, _ = select.select([JOY.fd], [], [], timeout)
    if not r: return
    for ev in JOY.read():
        # Listen to ALL standard stick axes now
        if ev.type == ecodes.EV_ABS and ev.code in (AX_LEFT_Y, AX_LEFT_X, AX_RIGHT_X, AX_RIGHT_Z):
            JOY_STATE['axes'][ev.code] = norm_axis(JOY, ev.code, ev.value)
        elif ev.type == ecodes.EV_KEY:
            if ev.value == 1: JOY_STATE['btn'].add(ev.code)
            elif ev.value == 0: JOY_STATE['btn'].discard(ev.code)

def button_just_pressed(code, now_ms, name):
    if (code in JOY_STATE['btn']) and (code not in PREV_BTN) and (now_ms - last_toggle[name] > DEBOUNCE_MS):
        last_toggle[name] = now_ms
        return True
    return False

def brake_active():
    # Stripped out the axis triggers to prevent Logitech Right-Stick overlap.
    # Now ONLY the X button (South Button) acts as the brake.
    return (BTN_CROSS in JOY_STATE['btn'])

def get_target_speeds():
    """
    Standard Differential Drive mapping.
    Left Stick Y: Forward / Reverse
    Right Stick X: Left / Right Steering
    """
    # 1. Get Linear Velocity (v) from Left Stick Y
    v = -JOY_STATE['axes'].get(AX_LEFT_Y, 0.0)

    # 2. Get Angular Velocity (omega) from Right Stick
    # We check both RX and Z because Logitech controllers switch mappings
    # depending on the D/X switch on the back.
    omega = JOY_STATE['axes'].get(AX_RIGHT_X, 0.0)
    if abs(JOY_STATE['axes'].get(AX_RIGHT_Z, 0.0)) > abs(omega):
        omega = JOY_STATE['axes'].get(AX_RIGHT_Z, 0.0)

    # 3. Apply Differential Kinematics
    vL_norm = v + omega
    vR_norm = v - omega

    # 4. Normalize to prevent radius clipping if pushing full diagonal
    max_mag = max(abs(vL_norm), abs(vR_norm))
    if max_mag > 1.0:
        vL_norm /= max_mag
        vR_norm /= max_mag

    # 5. Scale to actual motor speeds
    base_speed = 750 * LEVEL

    return int(vL_norm * base_speed), int(vR_norm * base_speed)

# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
def main():
    global JOY, LEVEL, PREV_BTN

    motors = ST3215Controller(PORT, BAUD)
    print("Configuring motors to Continuous Mode...")
    motors.set_operating_mode(LEFT_ID, 1)
    motors.set_operating_mode(RIGHT_ID, 1)
    motors.stop()

    JOY = find_joystick()
    if JOY:
        print(f"[JOY] Connected: {JOY.name}")
        try: JOY.grab()
        except: pass
    else:
        print("[ERROR] No gamepad found. Exiting.")
        return

    print(f"Ready to drive. Speed Level: {LEVEL}/4")

    try:
        while True:
            now_ms = time.time() * 1000.0
            poll_joystick(0.0)

            # --- Handle Speed Level Buttons (R1/L1) ---
            if button_just_pressed(BTN_R1, now_ms, 'r1'):
                if LEVEL < 4: LEVEL += 1
                print(f"[SPEED] Level {LEVEL}")
            if button_just_pressed(BTN_L1, now_ms, 'l1'):
                if LEVEL > 1: LEVEL -= 1
                print(f"[SPEED] Level {LEVEL}")

            # --- Handle Quit Button (Square) ---
            if button_just_pressed(BTN_SQUARE, now_ms, 'quit'):
                print("Quit requested.")
                break

            # --- Calculate and Apply Speeds ---
            if brake_active():
                vL, vR = 0, 0
            else:
                vL, vR = get_target_speeds()

            motors.sync_write_velocity(vL, vR)

            PREV_BTN = set(JOY_STATE['btn'])
            time.sleep(0.01) # 100Hz control loop

    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down safely...")
        motors.stop()
        if JOY:
            try: JOY.ungrab()
            except: pass
        motors.ser.close()

if __name__ == "__main__":
    main()
