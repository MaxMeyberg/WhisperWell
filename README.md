# WhisperWell – AI Therapy Platform 

An AI-powered emotion detection application that analyzes facial expressions in real-time and provides insights.

## Installation Guide

### Prerequisites
- Python 3.9+ 
- Node.js 16+ (for frontend)
- Mac with M-series chip or Intel processor

### Backend Setup

1. **Create and activate the virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   # Update pip
   pip install --upgrade pip

   # For Mac M-series chips (M1/M2/M3):
   pip install tensorflow-macos==2.16.2 

   # For Intel/Windows/Linux:
   # pip install tensorflow==2.16.2

   # Install face detection packages
   pip install mtcnn deepface opencv-python

   # Install API packages
   pip install flask flask-cors python-dotenv

   # Install Keras compatibility
   pip install tf-keras
   ```

3. **Verify installation**
   ```bash
   python -c "import cv2; import tensorflow as tf; import mtcnn; from deepface import DeepFace; print('Setup successful!')"
   ```

4. **Start the backend**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

## Troubleshooting

- **ModuleNotFoundError for cv2**: Run `pip install opencv-python` in your activated venv
- **TensorFlow version conflicts**: Use `pip uninstall -y tensorflow tensorflow-macos` then install the correct version for your system
- **DeepFace errors**: Make sure tf-keras is installed with `pip install tf-keras`

## Development
The project uses a Flask backend for face detection/emotion analysis and a React frontend for visualization.
