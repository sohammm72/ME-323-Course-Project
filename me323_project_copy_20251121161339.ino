#Arduino code

// Arduino + TB6600 Stepper Motor Driver
// Command-based motion control with Emergency Stop ('s')
// Uses theoretical calculation for steps/mm based on hardware specs.

// --- Pin Definitions ---
const int dirPin = 2;  // Direction Pin
const int pulPin = 3;  // Pulse Pin

// ===================================================================
// --- Hardware Configuration (IMPORTANT: VERIFY THESE VALUES) ---
// ===================================================================
const int MOTOR_STEPS_PER_REV = 200;    // Standard for NEMA 17 (1.8°/step)
const int DRIVER_MICROSTEPS   = 1;      // CHECK THE DIP SWITCHES ON YOUR TB6600!
const float LEAD_SCREW_PITCH_MM = 1.5f; // You specified 1mm pitch

// --- Calculated Steps per Millimeter (Do not change this line) ---
// const float STEPS_PER_MM = (MOTOR_STEPS_PER_REV * DRIVER_MICROSTEPS) / LEAD_SCREW_PITCH_MM;
const float STEPS_PER_MM = 160.0f; // <--- CORRECT CALIBRATED VALUE
// ===================================================================

// --- Global Position Tracking ---
long stepCount = 0;   // Use 'long' to avoid overflow on long moves
float currentPosition_mm = 0.0f;

void setup() {
  pinMode(dirPin, OUTPUT);
  pinMode(pulPin, OUTPUT);
  Serial.begin(115200);

  // --- Welcome Message ---
  Serial.println("\n--- Stepper Motor Control ---");
  Serial.println("Ready for commands.");
  Serial.print("Calculated Steps/mm: ");
  Serial.println(STEPS_PER_MM); // Using the new calculated value
  Serial.println("Format: direction,distance,speed");
  Serial.println("Example: r,50,10 (Right, 50mm, 10mm/s)");
  Serial.println("Enter 's' at any time for EMERGENCY STOP.");
  Serial.println("---------------------------");
  Serial.print("Current Position: ");
  Serial.println(currentPosition_mm, 3);
}

void loop() {
  // Check if a complete command line is available in the serial buffer
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Remove any leading/trailing whitespace

    if (command.length() > 0) {
      if (command == "s") {
        Serial.println("Motor is already stopped.");
      } else {
        Serial.print("\nReceived command: [");
        Serial.print(command);
        Serial.println("]");
        parseAndExecute(command);
      }
    }
  }
}

/**
 * @brief Parses a command string and calls the moveMotor function.
 * @param command The input string, e.g., "r,50,10"
 */
void parseAndExecute(String command) {
  int firstComma = command.indexOf(',');
  int secondComma = command.indexOf(',', firstComma + 1);

  if (firstComma == -1 || secondComma == -1) {
    Serial.println("Error: Invalid command format. Expected two commas.");
    return;
  }

  String dirStr = command.substring(0, firstComma);
  String distStr = command.substring(firstComma + 1, secondComma);
  String speedStr = command.substring(secondComma + 1);

  char direction = dirStr.charAt(0);
  float distance_mm = distStr.toFloat();
  float speed_mm_s = speedStr.toFloat();

  if ((direction != 'l' && direction != 'r') || distance_mm <= 0 || speed_mm_s <= 0) {
    Serial.println("Error: Invalid parameters.");
    Serial.println(" - Direction must be 'l' or 'r'.");
    Serial.println(" - Distance and Speed must be positive numbers.");
    return;
  }

  moveMotor(direction, distance_mm, speed_mm_s);
}

/**
 * @brief Moves the motor a specific distance at a specific speed.
 * @param direction 'l' for left, 'r' for right.
 * @param distance_mm The distance to travel in millimeters.
 * @param speed_mm_s The target speed in mm/s.
 */
void moveMotor(char direction, float distance_mm, float speed_mm_s) {
  if (direction == 'r') {
    digitalWrite(dirPin, LOW);
    Serial.println("Direction: Right");
  } else {
    digitalWrite(dirPin, HIGH);
    Serial.println("Direction: Left");
  }

  // REPLACED 'stepsPerMM_actual' with the new calculated 'STEPS_PER_MM'
  long stepsToGo = (long)(distance_mm * STEPS_PER_MM + 0.5f);
  float delay_float = 1000000.0f / (2.0f * speed_mm_s * STEPS_PER_MM);
  int stepDelay_us = (int)(delay_float + 0.5f);
  
  if (stepDelay_us < 50) {
     stepDelay_us = 50;
     Serial.println("Warning: Speed is very high. Capping step delay to 50us.");
  }

  Serial.print("Target Distance: "); Serial.print(distance_mm, 3); Serial.println(" mm");
  Serial.print("Target Speed: "); Serial.print(speed_mm_s, 3); Serial.println(" mm/s");
  Serial.print("Calculated Steps: "); Serial.println(stepsToGo);
  Serial.print("Calculated Step Delay: "); Serial.print(stepDelay_us); Serial.println(" us");

  Serial.println("--- MOVING (send 's' to stop) ---");

  bool moveAborted = false; 
  
  for (long i = 0; i < stepsToGo; i++) {
    digitalWrite(pulPin, HIGH);
    delayMicroseconds(stepDelay_us);
    digitalWrite(pulPin, LOW);
    delayMicroseconds(stepDelay_us);

    if (direction == 'r') {
      stepCount--;
    } else {
      stepCount++;
    }

    if (Serial.available() > 0) {
      char commandChar = Serial.read();
      if (commandChar == 's') {
        moveAborted = true;
        while(Serial.available() > 0) { Serial.read(); }
        break;
      }
    }
  }

  // REPLACED 'stepsPerMM_actual' with the new calculated 'STEPS_PER_MM'
  currentPosition_mm = stepCount / STEPS_PER_MM;

  if (moveAborted) {
    Serial.println("\n!!! EMERGENCY STOPPED !!!");
  } else {
    Serial.println("--- MOVE COMPLETE ---");
  }
  
  Serial.print("New Position: ");
  Serial.print(currentPosition_mm, 3);
  Serial.println(" mm");
  Serial.println("---------------------------");
}