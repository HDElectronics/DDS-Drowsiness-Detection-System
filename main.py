import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import subprocess
from datetime import datetime
import EmailClient  # Assuming this is a custom module for sending emails
from time import time
import json


def load_config(path):
    """Load the config.json file

    Args:
        path (str): the absolute path of the "config.json" file

    Returns:
        dict: A dictionary of all the configurations and paths needed to execute the script
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
alarm_sound_path = config['alert_settings']['alarm_sound_path']

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
    # Calculate the Euclidean distances between the landmarks of the eye
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # Calculate the Euclidean distance of the eye itself
    C = dist.euclidean(eye[0], eye[3])
    # Compute the EAR ratio
    ear = (A + B) / (2.0 * C)
    return ear

# Load the pre-trained face detector and facial landmark predictor from dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Start video capture
cap = cv2.VideoCapture("/dev/video0")
# Set a lower resolution for better performance
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Counters
frame_counter = 0
drowsy = False

# Timers
current_time = 0
sent_email_time = 0


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Detect faces in the grayscale frame
    faces = detector(gray, 0)

    # Loop over each detected face
    for face in faces:
        # Predict facial landmarks for the face
        shape = predictor(gray, face)
        points = np.zeros((68, 2), dtype=int)
        
        # Extract the coordinates of the facial landmarks
        for i in range(68):
            points[i] = (shape.part(i).x, shape.part(i).y)

        # Extract the landmarks for the left and right eyes
        leftEye = points[42:48]
        rightEye = points[36:42]
        # Calculate the EAR for each eye
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        # Compute the average EAR for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        # Draw contours around the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        # Check if the EAR is below the threshold
        if ear < EYE_AR_THRESH:
            frame_counter += 1
            # If the eyes have been closed for a certain number of frames
            if frame_counter >= EYE_AR_CONSEC_FRAMES:
                if not drowsy:
                    print("Drowsiness detected!")
                    drowsy = True
                    # Display "DROWSY!" on the frame
                    cv2.putText(frame, "DROWSY!", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                    # Get the current time
                    current_time = time()
                    # If it's been longer than the specified email sending frequency since the last email was sent
                    if current_time - sent_email_time > email_sending_freq:
                        # Get current time in a specific format
                        now = datetime.now()
                        time_string = now.strftime("%Y-%m-%d %H:%M:%S")
                        # Capture an image to attach to the email
                        cv2.imwrite(f"captures/image_{time_string}.png", frame)
                        image_path = f"captures/image_{time_string}.png"
                        sent_email_time = time()
                        
                        # Send an email with the captured image
                        EmailClient.send_email(recepient_email, recepient_name, image_path)
                        print("Take capture and send email!")

                    # Play an alarm sound when drowsiness is detected
                    afplay_process = subprocess.Popen(["aplay", alarm_sound_path])

        else:
            # Reset the frame counter and drowsy flag if the eyes are open
            frame_counter = 0
            drowsy = False

        # Display the EAR value on the frame
        cv2.putText(frame, f"EAR: {ear:.2f}", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the frame
    cv2.imshow("Frame", frame)
    # Check for 'q' key press to quit the loop
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
