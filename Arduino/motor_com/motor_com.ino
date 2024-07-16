// Define pin assignments for the L293D motor driver
int forwardPin = 9;  // Arduino pin connected to L293D Input 1
int backwardPin = 10; // Arduino pin connected to L293D Input 2
int motorSpeedPin = 11; // Arduino PWM pin connected to L293D Enable 1,2 for speed control

void setup() {
  // Set motor control pins as outputs
  pinMode(forwardPin, OUTPUT);
  pinMode(backwardPin, OUTPUT);
  pinMode(motorSpeedPin, OUTPUT);

  // Initialize serial communication at 9600 bps
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Trim whitespace and newline

    // Check if command starts with "FORWARD" or "BACKWARD"
    if (command.startsWith("FORWARD ")) {
      int time = command.substring(8).toInt(); // Get the duration from the command
      moveMotor(forwardPin, backwardPin, time);
    } else if (command.startsWith("BACKWARD ")) {
      int time = command.substring(9).toInt(); // Get the duration from the command
      moveMotor(backwardPin, forwardPin, time);
    }
  }
}

void moveMotor(int pinHigh, int pinLow, int duration) {
  analogWrite(motorSpeedPin, 255); // Set motor to full speed or adjust as needed
  digitalWrite(pinHigh, HIGH);
  digitalWrite(pinLow, LOW);
  delay(duration * 1000); // Convert seconds to milliseconds

  // Stop the motor after the duration
  digitalWrite(pinHigh, LOW);
  digitalWrite(pinLow, LOW);
  analogWrite(motorSpeedPin, 0);
}

