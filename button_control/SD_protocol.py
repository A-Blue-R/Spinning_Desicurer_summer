import serial
import time

# Establish serial connection
# ser = serial.Serial('/dev/ttyACM0', 9600) 
ser = serial.Serial('COM3', 9600) 
time.sleep(2)  # Wait for the connection to establish

def send_command(movement, motor_duration, led_duration):
    command = f"{movement} {motor_duration} LED {led_duration}"
    ser.write((command + '\n').encode())
    print(f"Command sent: {command}")

one_minute = 6
two_minute = 12 

def main_loop():
    while True:
        print("Press Button Twice to Start")
        while ser.readline().decode('utf-8').strip() != 'CONTINUE':
            pass  # Wait for button press signal from Arduino
        
        send_command("FORWARD", two_minute, 0)
        time.sleep(two_minute + 1)
        
        send_command("FORWARD", one_minute, one_minute)
        time.sleep(one_minute + 1)
        
        print("Rotate Device")
        print("Press Button for Next Step")
        while ser.readline().decode('utf-8').strip() != 'CONTINUE':
            pass  # Wait for button press signal from Arduino

        send_command("FORWARD", one_minute, one_minute)
        time.sleep(one_minute + 1)
        
        send_command("FORWARD", two_minute, 0)
        time.sleep(two_minute + 1)

        print("Cycle Complete")
        if ser.readline().decode('utf-8').strip() == 'STOP':
            break  # Exit the loop if 'STOP' is received

    print("Finished")
    ser.close()

if __name__ == '__main__':
    main_loop()
