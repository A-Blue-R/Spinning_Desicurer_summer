import serial
import time
import keyboard  # Import the keyboard module

# Establish a connection to the Arduino
ser = serial.Serial('COM3', 9600)  # Replace 'COM3' with your actual COM port
time.sleep(2)  # Wait for the connection to establish

def send_command(movement, motor_duration, led_duration):
    command = f"{movement} {motor_duration} LED {led_duration}"
    ser.write((command + '\n').encode())
    print(f"Command sent: {command}")  # Print the command for debugging

# SD Protocol
one_minute = 6
two_minute = 12 

send_command("FORWARD", two_minute, 0)  # Move forward for 5 seconds and LED on for 3 seconds

time.sleep(two_minute)
time.sleep(1)

send_command("FORWARD", one_minute, one_minute)

time.sleep(one_minute)
time.sleep(1)

print("Press spacebar to proceed...")
keyboard.wait('space')  # This will pause the script until spacebar is pressed
        
send_command("FORWARD", one_minute, one_minute)
        
time.sleep(one_minute)
time.sleep(1)
        
send_command("FORWARD", two_minute, 0)
time.sleep(two_minute)
time.sleep(1)

print("Finished")

ser.close()  # Close the serial connection
