#include <Arduino.h>

int ledPin = 5;
int motorDirectionPin = 12;
int motorSpeedPin = 10;
int buzzerPin = 4;  // Buzzer connected to pin D4
int buttonPin = 2;  // Button connected to pin D2

unsigned long startMillis;
unsigned long ledStartMillis;
int duration;
int ledDuration;
bool motorRunning = false;
bool ledOn = false;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(motorDirectionPin, OUTPUT);
  pinMode(motorSpeedPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    int index = command.indexOf(" LED ");
    if (index == -1) return;  // Return if format is incorrect

    if (command.startsWith("FORWARD ")) {
      duration = command.substring(8, index).toInt() * 1000;
      startMotor(HIGH);
    } else if (command.startsWith("BACKWARD ")) {
      duration = command.substring(9, index).toInt() * 1000;
      startMotor(LOW);
    }

    ledDuration = command.substring(index + 5).toInt() * 1000;
    startLED();
    soundBuzzer(500); // Sound buzzer for 500 ms
  }

  // Check to stop motor after duration
  if (motorRunning && millis() - startMillis > duration) {
    stopMotor();
  }

  // Check to turn off LED after duration
  if (ledOn && millis() - ledStartMillis > ledDuration) {
    stopLED();
  }

  // Check if button is pressed (assuming active low)
  if (digitalRead(buttonPin) == LOW) {
    delay(50); // Debounce delay
    if (digitalRead(buttonPin) == LOW) { // Confirm button is still pressed
      soundBuzzer(200); // Quick buzz to confirm button press
      Serial.println("CONTINUE"); // Send a continue signal to Python
    }
  }
}

void startMotor(bool direction) {
  digitalWrite(motorDirectionPin, direction);
  analogWrite(motorSpeedPin, 255);
  startMillis = millis();
  motorRunning = true;
}

void stopMotor() {
  analogWrite(motorSpeedPin, 0);
  motorRunning = false;
}

void startLED() {
  analogWrite(ledPin, 255);
  ledStartMillis = millis();
  ledOn = true;
}

void stopLED() {
  analogWrite(ledPin, 0);
  ledOn = false;
}

void soundBuzzer(int duration) {
  digitalWrite(buzzerPin, HIGH);
  delay(duration);
  digitalWrite(buzzerPin, LOW);
}
