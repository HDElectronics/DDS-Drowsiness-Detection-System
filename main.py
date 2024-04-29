import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import subprocess
from mailjet_rest import Client
from datetime import datetime
import EmailClient
from time import time
import json


def load_config(path):
    """Load the config.json file

    Args:
        path (str): the absolute path of the "config.json" file

    Returns:
        dict: A dictionnary of all the configs and path needed to execute the script
    """
    with open(path, 'r') as file:
        config = json.load(file)
    return config

config_path = 'config.json'
config = load_config(config_path)

# Email sender
recepient_email = config['email_settings']['recepient_email']

# Email receiver
recepient_name = config['email_settings']['recepient_name']

# Email sending frequency in seconds
email_sending_freq = config['email_settings']['email_sending_freq']

# Sound played during a drowsiness detection
alram_sound_path = config['alert_settings']['alarm_sound_path']

# Threshold for the eye aspect ratio indicating blink
EYE_AR_THRESH = config['alert_settings']['EYE_AR_THRESH']

# Frames the eye must be below the threshold
EYE_AR_CONSEC_FRAMES = config['alert_settings']['EYE_AR_CONSEC_FRAMES']



def eye_aspect_ratio(eye):
    """Calculate the EAR ratio

    Args:
        eye (list): Landmarks of the eye from dlib

    Returns:
        float: EAR ratio
    """
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Load the pre-trained face detector and facial landmark predictor from dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Set a lower width
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Set a lower height

# Counters
frame_counter = 0
drowsy = False

# Timers
current_time = 0
sent_email_time = 0


while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 0)

    for face in faces:
        shape = predictor(gray, face)
        points = np.zeros((68, 2), dtype=int)
        
        for i in range(68):
            points[i] = (shape.part(i).x, shape.part(i).y)

        leftEye = points[42:48]
        rightEye = points[36:42]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0

        # Draw the eyes using the landmarks
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            frame_counter += 1
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
                if not drowsy:
                    print("Drowsiness detected!")
                    drowsy = True
                    cv2.putText(frame, "DROWSY!", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    current_time = time()
                    if current_time - sent_email_time > email_sending_freq:
                        # Get current time
                        now = datetime.now()
                        time_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        # Capture the image to attache it to the email
                        cv2.imwrite(f"captures/image_{time_string}.png", frame)
                        image_path = f"captures/image_{time_string}.png"
                        sent_email_time = time()
                        
                        EmailClient.send_email(recepient_email, recepient_name, )
                        print("Take capture and send email!")

                    # Play an alarm sound when a Drowsiness is detected
                    afplay_process = subprocess.Popen(["afplay", alram_sound_path])

        else:
            frame_counter = 0
            drowsy = False

        # Display the result
        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
