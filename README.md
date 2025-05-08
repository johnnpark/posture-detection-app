# Posturite – Real-Time Posture Detection App

Posturite is a desktop application that uses computer vision to monitor and detect forward head posture in real time using the user’s webcam. It provides visual alerts and feedback to help maintain healthy posture habits, especially while working on a computer.

## Features

- Real-time posture detection using MediaPipe Pose Estimation
- Dynamic calibration scan based on user’s upright posture
- Fullscreen red alert overlay when poor posture is detected
- Rounded webcam feed display with smooth UI using Tkinter Canvas
- Start and End Session button controls
- Countdown screen prior to calibration with live feedback

## Technology Stack

- Python 3.11
- OpenCV
- MediaPipe
- Pillow (PIL)
- Tkinter

## How It Works

1. Click “Start Session”
2. A 3-second countdown begins, followed by a calibration scan while the user sits upright
3. The system records the Z-position of the nose as the baseline for good posture
4. During the session, it compares the current nose position against the baseline
5. If the head leans forward significantly, a fullscreen red overlay is triggered
6. When posture returns to normal, the alert is removed and a “Good Posture” message appears

## Getting Started

Clone the repository and install dependencies:

```bash
git clone https://github.com/johnnpark/posture-detection-app.git
cd posture-detection-app
pip install -r requirements.txt
python app.py

## **File Overview**

app.py - frontend logic, ui, and event flow
posture_detector.py - backend pose detection and calibration
IMG_A60BCABA778B-1.jpeg – Logo displayed in the top-left of the app
Hoohacks-7.jpg – Application background image
requirements.txt – Python package dependencies

## Author
John Park
Github: @johnnpark

