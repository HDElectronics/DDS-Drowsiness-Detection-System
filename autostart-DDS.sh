#!/bin/bash

# Write nameserver configurations to /etc/resolv.conf
sudo sh -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
sudo sh -c 'echo "nameserver 8.8.4.4" >> /etc/resolv.conf'

# Navigate to the directory and activate the virtual environment
cd /home/pi/DDS-Drowsiness-Detection-System
source .myvenv/bin/activate

# Run the Python script
python3 main.py
