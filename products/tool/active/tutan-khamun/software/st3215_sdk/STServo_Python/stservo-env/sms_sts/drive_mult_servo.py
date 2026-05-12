#!/usr/bin/env python

import sys
import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

sys.path.append("..")
from scservo_sdk import *

# Configurations
ID_2 = 2
ID_3 = 3
BAUDRATE = 1000000
DEVICENAME = '/dev/ttyACM1' 

SCS_MOVING_SPEED = 2400  # Base speed (Positive for CW, Negative for CCW)
SCS_MOVING_ACC = 50      # Acceleration

portHandler = PortHandler(DEVICENAME)
packetHandler = sms_sts(portHandler)
    
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()

if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    portHandler.closePort()
    quit()

# Set BOTH servos to Wheel Mode
packetHandler.WheelMode(ID_2)
packetHandler.WheelMode(ID_3)

print("""
--------------------------------------------------
  Dual Servo Control Started
--------------------------------------------------
  [Up Arrow]    or [W] : Both CW
  [Down Arrow]  or [S] : Both CCW
  [Right Arrow] or [D] : ID 2 CW  | ID 3 CCW
  [Left Arrow]  or [A] : ID 2 CCW | ID 3 CW
  [Spacebar]           : STOP MOTORS
  [Q]                  : Quit
--------------------------------------------------
""")

while True:
    ch = getch()
    
    speed_2 = 0
    speed_3 = 0
    update_motors = False

    # 1. Check for Arrow Keys (Escape Sequences)
    if ch == '\x1b':
        # Arrow keys send ESC (\x1b) followed by [ and A, B, C, or D
        ch2 = getch()
        if ch2 == '[':
            ch3 = getch()
            if ch3 == 'A':   # UP Arrow
                speed_2, speed_3 = SCS_MOVING_SPEED, -SCS_MOVING_SPEED
                update_motors = True
            elif ch3 == 'B': # DOWN Arrow
                speed_2, speed_3 = -SCS_MOVING_SPEED, SCS_MOVING_SPEED
                update_motors = True
            elif ch3 == 'C': # RIGHT Arrow
                speed_2, speed_3 = SCS_MOVING_SPEED, SCS_MOVING_SPEED
                update_motors = True
            elif ch3 == 'D': # LEFT Arrow
                speed_2, speed_3 = -SCS_MOVING_SPEED, -SCS_MOVING_SPEED
                update_motors = True
                
    # 2. Check for W, A, S, D fallback
    elif ch.lower() == 'w':
        speed_2, speed_3 = SCS_MOVING_SPEED, -SCS_MOVING_SPEED
        update_motors = True
    elif ch.lower() == 's':
        speed_2, speed_3 = -SCS_MOVING_SPEED, SCS_MOVING_SPEED
        update_motors = True
    elif ch.lower() == 'd':
        speed_2, speed_3 = SCS_MOVING_SPEED, SCS_MOVING_SPEED
        update_motors = True
    elif ch.lower() == 'a':
        speed_2, speed_3 = -SCS_MOVING_SPEED, -SCS_MOVING_SPEED
        update_motors = True

    # 3. Check for Stop / Quit
    elif ch == ' ':
        speed_2, speed_3 = 0, 0
        update_motors = True
    elif ch.lower() == 'q':
        print("\r\nExiting program...")
        break

    # 4. Write commands to servos if a valid key was pressed
    if update_motors:
        packetHandler.WriteSpec(ID_2, speed_2, SCS_MOVING_ACC)
        packetHandler.WriteSpec(ID_3, speed_3, SCS_MOVING_ACC)
        
        # Terminal feedback
        if speed_2 == 0 and speed_3 == 0:
            print("\rStatus: STOPPED                      ", end="")
        else:
            print(f"\rStatus: ID2={speed_2} | ID3={speed_3}       ", end="")

# Safely stop motors before closing port
packetHandler.WriteSpec(ID_2, 0, SCS_MOVING_ACC)
packetHandler.WriteSpec(ID_3, 0, SCS_MOVING_ACC)
portHandler.closePort()