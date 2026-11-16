import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from cvzone.SerialModule import SerialObject

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)
arduino = SerialObject("COM3")

FINGER_TIPS  = [4, 8, 12, 16, 20]
FINGER_BASES = [2, 5,  9, 13, 17]

def get_angles(lmList):
    angles = []
    for tip, base in zip(FINGER_TIPS, FINGER_BASES):
        ax, ay = lmList[tip][0],  lmList[tip][1]
        bx, by = lmList[base][0], lmList[base][1]
        dist = np.sqrt((ax - bx)**2 + (ay - by)**2)
        clamped = max(20, min(120, dist))
        angles.append(int((clamped - 20) / 100 * 180))
    return angles

last_angles = None

while True:
    success, image = cap.read()
    hands, bboxInfo = detector.findHands(image)
    if len(hands) == 1:
        angles = get_angles(hands[0]["lmList"])
        if angles != last_angles:
            arduino.sendData(angles)
            last_angles = angles
    cv2.imshow('image', image)
    cv2.waitKey(1)
