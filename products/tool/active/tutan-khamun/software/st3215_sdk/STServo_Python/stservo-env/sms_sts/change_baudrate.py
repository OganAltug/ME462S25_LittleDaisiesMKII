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


sys.path.append("..")
from scservo_sdk import *

# Configurations
SCS_ID = 2            # Current Servo ID
BAUDRATE = 115200    # CURRENT baudrate (to talk to it right now)
DEVICENAME = '/dev/ttyACM1' 

# NEW BAUDRATE INDEX
# 0: 1,000,000 | 1: 500,000 | 2: 250,000 | 3: 128,000 | 4: 115,200 | 5: 76,800 | 6: 57,600 | 7: 38,400
NEW_BAUD_INDEX = 0    # Example: Setting to 1000000 bps

# Initialize PortHandler instance
# Set the port path
# Get methods and members of PortHandlerLinux or PortHandlerWindows
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
# Get methods and members of Protocol
packetHandler = sms_sts(portHandler)
# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

# Set port baudrate
if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to set the baudrate")
else:
    print("Failed to set the baudrate")
    portHandler.closePort()
    quit()

# 1. Unlock EEPROM
scs_comm_result, scs_error = packetHandler.unLockEprom(SCS_ID)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))
    quit()

# 2. Write the new Baudrate Index to the Baudrate Register
# NOTE: If your SDK throws an error for 'SMS_STS_BAUD_RATE', replace it with the number 4
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(SCS_ID, SMS_STS_BAUD_RATE, NEW_BAUD_INDEX)

if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
else:
    # 3. Lock EEPROM to save
    packetHandler.LockEprom(SCS_ID)
    print(f"Succeeded to change the Servo Baudrate index to {NEW_BAUD_INDEX}")

if scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))
    quit()