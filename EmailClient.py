import base64
from mailjet_rest import Client
import os
from datetime import datetime

# Use your Mailjet keys
api_key = 'a8562b6b2995da46fff0cc214c7b324c'
api_secret = 'cba2c35f475fbecb25c92e2d7cd51c71'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')


def send_email(recipient_email, recipient_name, image_path):

    # Open and read the image file in binary mode
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Encode the image data to Base64
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # Get current time
    now = datetime.now()
    time_string = now.strftime("%Y-%m-%d %H:%M:%S")

    subject = "Drowsiness Detected!"
    message = f"A drowsiness has been detected on {time_string}, a picture is attached, please take an action!"

    # Email body in HTML format
    html_part = f"""
    <html>
        <head></head>
        <body>
            <h1 style="color: #ff6347;">Drowsiness Alert!</h1>
            <p>Dear Admin,</p>
            <p>A drowsiness event was detected on <strong>{time_string}</strong>. Please see the attached image for reference and take appropriate action.</p>
            <p>Stay safe,<br/>
            DDS - Drowsiness Detection System</p>
        </body>
    </html>
    """

    data = {
        'Messages': [
            {
                "From": {
                    "Email": "khadraouiibrahim@gmail.com",
                    "Name": "DDS - Drowsiness Detection System"
                },
                "To": [
                    {
                        "Email": recipient_email,
                        "Name": recipient_name
                    }
                ],
                "Subject": subject,
                "HTMLPart": html_part,
                "TextPart": message,
                "Attachments": [
                    {
                        "ContentType": "image/jpeg",
                        "Filename": os.path.basename(image_path),
                        "Base64Content": encoded_image
                    }
                ]
            }
        ]
    }

    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
