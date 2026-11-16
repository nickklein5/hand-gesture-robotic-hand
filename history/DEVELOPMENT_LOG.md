# Development log

Reconstructed from the working session in which the project was built (resume dates: July-August 2026). The git commits in this repo follow these stages; they are dated when the repo was created, not when each stage was first run.

1. **Baseline.** Single servo on pin 9. cvzone `fingersUp()` triggered 180 degrees for an index-finger-only gesture, otherwise 0. cvzone `SerialObject` / `SerialData` handled serial.
2. **Five servos.** Pins 3, 5, 6, 9, 10. Each finger's angle came from 2D fingertip-to-knuckle distance, with a change check to cut redundant serial writes.
3. **PySerial swap.** The cvzone Arduino library would not install (Library Manager had no result; the GitHub ZIP held no `.h` file; `library not valid` error). Replaced it with raw bytes: `arduino.write(bytes(angles))` in Python, `Serial.available() >= 5` and `Serial.read()` on the Arduino.
4. **Bug fixes during setup.** Installed `mediapipe` (missing cvzone dependency); installed libraries inside the PyCharm interpreter; confirmed the COM port.
5. **Joint angles.** Distance-based angles saturated when a finger curled toward the camera. Switched to the angle at the middle joint from three landmarks, then to 3D (x, y, z) with a clamped `acos`.
6. **Calibration.** The thumb stayed high in a closed fist, so added a two-pose (fist/open) per-finger min/max calibration, with the hold time set to 5 s.
7. **Sensitivity.** Values stuck at 180 near full extension, so applied a `normalized ** 0.5` curve.
8. **Power.** Moved from the Arduino 5V pin to a 6V / 1.5 A wall supply via an MB102 module, with shared ground and USB kept for data.

## Open items
- Measure frame rate and gesture-to-servo latency.
- Mount the servos on the physical hand and tune per-finger limits.
