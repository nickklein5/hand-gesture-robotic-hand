import cv2
import numpy as np
import math
from cvzone.HandTrackingModule import HandDetector
import serial

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)
arduino = serial.Serial("COM3", 9600)   # change to your Arduino's port

# (base knuckle, middle joint, fingertip) landmark indices per finger
FINGER_JOINTS = [
    (2,  3,  4),   # thumb
    (5,  6,  8),   # index
    (9,  10, 12),  # middle
    (13, 14, 16),  # ring
    (17, 18, 20),  # pinky
]

def get_finger_angle(lmList, a, b, c):
    ax, ay, az = lmList[a][0], lmList[a][1], lmList[a][2]
    bx, by, bz = lmList[b][0], lmList[b][1], lmList[b][2]
    cx, cy, cz = lmList[c][0], lmList[c][1], lmList[c][2]
    v1 = (ax - bx, ay - by, az - bz)
    v2 = (cx - bx, cy - by, cz - bz)
    dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
    if mag1 * mag2 == 0:
        return 0
    angle = math.degrees(math.acos(max(-1, min(1, dot / (mag1 * mag2)))))
    return int(angle)

# ---- calibration: hold a closed fist, then an open hand ----
def capture_pose(prompt, duration=5):
    print(prompt)
    readings = [[] for _ in range(5)]
    start = cv2.getTickCount()
    while True:
        elapsed = (cv2.getTickCount() - start) / cv2.getTickFrequency()
        remaining = int(duration - elapsed)
        success, image = cap.read()
        hands, _ = detector.findHands(image)
        cv2.putText(image, f"{prompt} ({remaining}s)", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if len(hands) == 1:
            lmList = hands[0]["lmList"]
            for i, (a, b, c) in enumerate(FINGER_JOINTS):
                readings[i].append(get_finger_angle(lmList, a, b, c))
        cv2.imshow("Calibration", image)
        cv2.waitKey(1)
        if elapsed >= duration:
            break
    return [sum(r) // len(r) if r else 90 for r in readings]

print("=== CALIBRATION ===")
closed = capture_pose("Make a CLOSED FIST", duration=5)
open_hand = capture_pose("Open hand FULLY FLAT", duration=5)

FINGER_MIN = closed       # joint angle when fully closed
FINGER_MAX = open_hand    # joint angle when fully open
print(f"Min (closed): {FINGER_MIN}")
print(f"Max (open):   {FINGER_MAX}")

def get_angles(lmList):
    angles = []
    for i, (a, b, c) in enumerate(FINGER_JOINTS):
        angle = get_finger_angle(lmList, a, b, c)
        lo, hi = FINGER_MIN[i], FINGER_MAX[i]
        if hi == lo:
            angles.append(0)
            continue
        clamped = max(lo, min(hi, angle))
        normalized = (clamped - lo) / (hi - lo)   # 0.0 to 1.0
        curved = normalized ** 0.5                # sqrt curve: more sensitivity near full extension
        angles.append(int(curved * 180))
    return angles

last_angles = None

while True:
    success, image = cap.read()
    hands, bboxInfo = detector.findHands(image)
    if len(hands) == 1:
        angles = get_angles(hands[0]["lmList"])
        print(angles)
        if angles != last_angles:             # only send on change
            arduino.write(bytes(angles))
            last_angles = angles
    cv2.imshow('image', image)
    cv2.waitKey(1)
