import cv2
import numpy as np
import math
from cvzone.HandTrackingModule import HandDetector
import serial

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)
arduino = serial.Serial("COM3", 9600)

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

def get_angles(lmList):
    angles = []
    for a, b, c in FINGER_JOINTS:
        angle = get_finger_angle(lmList, a, b, c)
        clamped = max(20, min(170, angle))
        angles.append(int((clamped - 20) / 150 * 180))
    return angles

last_angles = None

while True:
    success, image = cap.read()
    hands, bboxInfo = detector.findHands(image)
    if len(hands) == 1:
        angles = get_angles(hands[0]["lmList"])
        print(angles)
        if angles != last_angles:
            arduino.write(bytes(angles))
            last_angles = angles
    cv2.imshow('image', image)
    cv2.waitKey(1)
