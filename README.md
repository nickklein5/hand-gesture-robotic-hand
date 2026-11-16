# Hand Gesture Controlled Robotic Hand

Real-time system that tracks a hand through a webcam and mirrors each finger's
flexion on five servo motors via an Arduino.

**Stack:** Python, OpenCV, MediaPipe (via cvzone), PySerial, C++ (Arduino, `Servo.h`)

## How it works

1. **Capture + landmarks.** OpenCV grabs webcam frames; cvzone/MediaPipe returns 21 3D hand landmarks per frame.
2. **Joint-angle math.** For each finger, three landmarks (base knuckle, middle joint, fingertip) form two 3D vectors from the middle joint. The joint angle is `acos(dot(v1, v2) / (|v1||v2|))`. Using x/y/z makes the reading much less dependent on camera distance and hand orientation than raw tip-to-base distance.
3. **Calibration.** On launch you hold a closed fist, then an open hand (5 s each). The average joint angle of each finger becomes that finger's min/max, which is mapped to a 0-180 servo angle.
4. **Sensitivity curve.** The normalized value is raised to the 0.5 power so small curls near full extension register sooner.
5. **Serial link.** Five angles (0-180) are sent as 5 raw bytes over USB serial at 9600 baud, only when they change.
6. **Firmware.** The Arduino waits for 5 bytes and writes each to its servo with `Servo.h` (PWM).

## Hardware

| Servo | Finger | Arduino pin |
|-------|--------|-------------|
| 0 | Thumb  | 3  |
| 1 | Index  | 5  |
| 2 | Middle | 6  |
| 3 | Ring   | 9  |
| 4 | Pinky  | 10 |

- Servo signal (orange) to the pin above; servo power (red) to the external 5V rail; servo ground (brown) to the GND rail.
- Servos are powered from an external 6V / 1.5 A wall supply through an Elegoo MB102 breadboard power module, not from the Arduino's 5V pin.
- **Arduino GND must be tied to the external supply's GND** (shared ground).
- The Arduino stays connected to the computer over USB for serial data.

## Setup

1. Install the libraries: `pip install -r requirements.txt`
2. Open `arduino/hand_servo/hand_servo.ino` in Arduino IDE, select the board and port, and upload.
3. Close the Arduino Serial Monitor (it holds the COM port).
4. Set the COM port in `hand_servo.py` (`serial.Serial("COM3", 9600)`) to match Tools > Port.
5. Run `python hand_servo.py`, complete the two calibration poses, then move your hand.

## Notes

- Best accuracy with the palm facing the camera. Edge-on hands and fingers pointing straight at the camera degrade the angle estimate.
- The calibration range, `0.5` curve exponent and 9600 baud rate are easy to tune.
- See `history/DEVELOPMENT_LOG.md` for how the project evolved.
