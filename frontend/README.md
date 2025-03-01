# WhisperWell - AI Emotion Detection

An AI-powered application that detects and analyzes facial emotions in real-time.

## Mac Setup Guide

### Prerequisites

#### 1. Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python 3
```bash
brew install python
```

#### 3. Install Node.js and npm
```bash
brew install node
```

#### 4. Install Git (if not already installed)
```bash
brew install git
```

### Project Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AI_Therapist-Nina.git
cd AI_Therapist-Nina
```

#### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create logs directory for face detection
mkdir -p logs
touch logs/face_detection.log
```

#### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### Running the Application

#### 1. Start the Backend Server
In one terminal:
```bash
cd backend
source venv/bin/activate
python app.py
```

#### 2. Start the Face Detection Monitor
In a second terminal:
```bash
cd backend
source venv/bin/activate
python -m dev_loggers.monitor_face_detection
```

#### 3. Start the Frontend
In a third terminal:
```bash
cd frontend
npm start
```

The application should now be running at http://localhost:3000

## Features

- **Facial Emotion Detection**: Analyzes facial expressions in real-time
- **Emotion Tracking**: Monitors changes in emotions over time
- **Interactive UI**: User-friendly interface for emotion feedback

## Tech Stack

### Frontend
- React.js
- HTML/CSS
- JavaScript

### Backend
- Python 3
- Flask (REST API)
- OpenCV (Computer Vision)
- DeepFace (Emotion Detection)
- TensorFlow (Machine Learning)

## Troubleshooting

### Camera Access
- Make sure to grant camera permissions to your browser when prompted
- If using Safari, ensure camera access is enabled in preferences

### Python Package Issues
If you encounter issues with specific packages:
```bash
pip install opencv-python  # For OpenCV
pip install deepface tensorflow  # For facial emotion detection
```

### Black Images in Face Detection
If you see black images in face detection:
- Ensure your webcam is working properly
- Check that your browser has permission to access the camera
- Try adjusting your lighting

### Emotion Detection Not Working
If emotion detection isn't working:
- Check the face detection log for errors: `backend/logs/face_detection.log`
- Make sure your face is clearly visible in good lighting
- Try restarting both the backend server and monitor

## Commands Reference

### Frontend

```bash
# Start the React development server
npm start

# Create a production build
npm run build

# Run tests
npm test
```

### Backend

```bash
# Start the Flask server
python app.py

# Start the emotion monitor
python -m dev_loggers.monitor_face_detection
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

