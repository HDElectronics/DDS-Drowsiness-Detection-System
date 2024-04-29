# Drowsiness Detection System

This project implements a drowsiness detection system using Python, OpenCV, dlib, and the Mailjet API. When drowsiness is detected, it alerts the user visually, plays a sound, and sends an email notification with a photo capture.

## Prerequisites

Before you begin, ensure you have Python installed on your system. You can download Python from [python.org](https://www.python.org/downloads/).

## Installation

Clone the repository:

```bash
git clone https://your-repository-url.git
cd your-project-directory
```

Create a virtual environment:
```bash
python -m venv myvenv
```

Activate the virtual environment:
   On Windows:
```bash
.\myvenv\Scripts\activate
On MacOS/Linux:
source myvenv/bin/activate
```

Install required packages:
```bash
pip install -r requirements.txt
```

Download the shape_predictor_68_face_landmarks.dat
```bash
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 && bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
```

## Configuration

Edit the `config.json` file to set up the email settings and alert thresholds:
```json
{
  "email_settings": {
    "recepient_email": "example@example.com",
    "recepient_name": "Admin",
    "email_sending_freq": 300
  },
  "alert_settings": {
    "alarm_sound_path": "alarm_sound.wav",
    "EYE_AR_THRESH": 0.23,
    "EYE_AR_CONSEC_FRAMES": 20
  }
}
```

## Running the System

To run the system, use the following command:
python main.py

The system will start monitoring in real-time using your webcam. Press `q` to quit the application.

## Code Overview

- main.py: This is the main script of the project. It initializes the camera, processes video frames to detect drowsiness using facial landmarks, and handles alerting logic.
- EmailClient.py: This script contains the functionality to send emails via the Mailjet API. It attaches a photo of the user when drowsiness is detected.
- config.json: A configuration file to manage email settings and drowsiness detection thresholds.

## Additional Information

- shape_predictor_68_face_landmarks.dat: Pre-trained model for facial landmark detection.
- captures/: Directory where images are saved when drowsiness is detected.

For more information or troubleshooting, refer to the official documentation of the libraries used like OpenCV, dlib, and Mailjet.
