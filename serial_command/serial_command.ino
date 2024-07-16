int ledPin = 5; // PWM pin for the LED
int forwardPin = 9; // Motor forward pin
int backwardPin = 10; // Motor backward pin
int motorSpeedPin = 11; // PWM pin for motor speed control

unsigned long startMillis; // Start time for motor actions
unsigned long ledStartMillis; // Start time for LED actions
int duration; // Duration for motor action
int ledDuration; // Duration for LED action
bool motorRunning = false; // State of the motor
bool ledOn = false; // State of the LED

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(forwardPin, OUTPUT);
  pinMode(backwardPin, OUTPUT);
  pinMode(motorSpeedPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    // Handling motor commands
    if (command.startsWith("FORWARD ")) {
      int index = command.indexOf(" LED ");
      duration = command.substring(8, index).toInt() * 1000; // Convert to milliseconds
      startMotor(forwardPin, backwardPin);
      ledDuration = command.substring(index + 5).toInt() * 1000; // Extract LED duration
      startLED();
    } else if (command.startsWith("BACKWARD ")) {
      int index = command.indexOf(" LED ");
      duration = command.substring(9, index).toInt() * 1000; // Convert to milliseconds
      startMotor(backwardPin, forwardPin);
      ledDuration = command.substring(index + 5).toInt() * 1000; // Extract LED duration
      startLED();
    }
  }

  // Check to stop motor after duration
  if (motorRunning && millis() - startMillis > duration) {
    stopMotor();
  }

  // Check to turn off LED after duration
  if (ledOn && millis() - ledStartMillis > ledDuration) {
    stopLED();
  }
}

void startMotor(int pinHigh, int pinLow) {
  analogWrite(motorSpeedPin, 255); // Set motor speed to maximum
  digitalWrite(pinHigh, HIGH);
  digitalWrite(pinLow, LOW);
  startMillis = millis(); // Record start time
  motorRunning = true; // Set motor state to running
}

void stopMotor() {
  digitalWrite(forwardPin, LOW);
  digitalWrite(backwardPin, LOW);
  analogWrite(motorSpeedPin, 0); // Stop the motor
  motorRunning = false; // Set motor state to not running
}

void startLED() {
  analogWrite(ledPin, 255); // Turn LED on to full brightness
  ledStartMillis = millis(); // Record start time for LED
  ledOn = true; // Set LED state to on
}

void stopLED() {
  analogWrite(ledPin, 0); // Turn LED off
  ledOn = false; // Set LED state to off
}
