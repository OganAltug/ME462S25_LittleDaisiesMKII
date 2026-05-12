from machine import Pin, PWM
import time
import sys
import select

class DualServoController:
    def __init__(self, pin_left=16, pin_right=17, freq=50, min_us=500, max_us=2500, max_angle=270):
        """
        Initializes the dual servo controller for 270-degree servos.
        Left servo is on pin 16, Right servo is on pin 17.
        """
        self.freq = freq
        self.min_us = min_us
        self.max_us = max_us
        self.max_angle = max_angle
        
        # Initialize PWM objects
        self.servo_left = PWM(Pin(pin_left))
        self.servo_right = PWM(Pin(pin_right))
        
        self.servo_left.freq(self.freq)
        self.servo_right.freq(self.freq)

    def _angle_to_duty(self, angle):
        """Converts an angle in degrees to a 16-bit PWM duty cycle."""
        # Clamp angle between 0 and max_angle
        angle = max(0, min(angle, self.max_angle))
        
        # Map angle to pulse width in microseconds
        pulse_us = self.min_us + (angle / self.max_angle) * (self.max_us - self.min_us)
        
        # Convert pulse width to 16-bit duty cycle (0-65535)
        period_us = 1000000 // self.freq
        duty = int((pulse_us / period_us) * 65535)
        return duty

    def set_angles(self, theta_left, theta_right):
        """Applies specific angles to the left and right servos."""
        self.servo_left.duty_u16(self._angle_to_duty(theta_left))
        self.servo_right.duty_u16(self._angle_to_duty(theta_right))

    def deinit(self):
        """Turns off the PWM signal, allowing the servos to go limp."""
        self.servo_left.deinit()
        self.servo_right.deinit()

# ==========================================
# Terminal Control Execution
# ==========================================

def run_terminal_control():
    # Initialize the gripper
    gripper = DualServoController(pin_left=16, pin_right=17)
    
    # 1500 us corresponds exactly to 135 degrees on a 270-degree servo 
    # (Range: 500us to 2500us)
    center_angle = 135.0
    
    angle_left = center_angle
    angle_right = center_angle
    
    # Send to starting position
    gripper.set_angles(angle_left, angle_right)
    
    print("--- Active Gripper Terminal Control ---")
    print("Status: Centered at 1500 us (135°)")
    print("Controls:")
    print("  [ w ] : Right CCW (+), Left CW (-)")
    print("  [ s ] : Right CW (-), Left CCW (+)")
    print("  [ q ] : Quit and power down servos")
    print("-" * 39)
    
    # Set up the poll object to read terminal input without blocking the loop
    poll_obj = select.poll()
    poll_obj.register(sys.stdin, select.POLLIN)
    
    try:
        while True:
            # Check if there is a character waiting in the terminal
            if poll_obj.poll(0):
                ch = sys.stdin.read(1).lower() # Read and convert to lowercase
                
                if ch == 'w':  
                    # 'w' key pressed
                    angle_right += 2  # Counter-Clockwise
                    angle_left -= 2   # Clockwise
                    
                elif ch == 's':  
                    # 's' key pressed
                    angle_right -= 2  # Clockwise
                    angle_left += 2   # Counter-Clockwise
                
                elif ch == 'q':
                    print("Quitting sequence initiated...")
                    break
                
                # Apply Constraints: Maximum +/- 20 degrees from the center position
                angle_right = max(center_angle - 20, min(angle_right, center_angle + 20))
                angle_left = max(center_angle - 20, min(angle_left, center_angle + 20))
                
                # Execute the move
                gripper.set_angles(angle_left, angle_right)
                
                # Print the live status
                print(f"Left Servo: {angle_left:.1f}° | Right Servo: {angle_right:.1f}°")
                
            # A tiny sleep to prevent the loop from hogging the CPU
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
        
    finally:
        # Always clean up the PWM signals when done
        gripper.deinit()
        print("Servos powered down safely.")

# Run the script
if __name__ == "__main__":
    run_terminal_control()