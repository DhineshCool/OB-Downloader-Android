#!/bin/bash

# Variables
VENV_DIR="myenv"

# Create a virtual environment
python3 -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
python3 -m pip install mutagen ffmpeg yt-dlp termcolor gdown rclone

# Deactivate the virtual environment
deactivate

echo "Dependencies installed successfully in the virtual environment."
