# WhisperWell AI Therapy Assistant

WhisperWell is an AI-powered therapy assistant that uses facial recognition, voice synthesis, and natural language processing to provide an interactive therapy experience.

## Features

- 🎭 Real-time emotion detection through facial recognition
- 🗣️ Natural conversation with AI therapist characters
- 🔊 Voice synthesis for spoken responses
- 📝 Memory of conversation context
- 🖼️ Dynamic character image generation based on conversation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A webcam for facial recognition features
- Modern web browser (Chrome, Firefox, Safari)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MaxMeyberg/AI_Therapist-Nina.git
   cd AI_Therapist-Nina
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   # Never tested it on windows
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the backend directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   BLACK_FOREST_API_KEY=your_black_forest_key
   ```

## Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python app.py
   ```
   The server will start on `http://localhost:5001`

2. **Start the Frontend Development Server**
   In a new terminal:
   ```bash
   cd frontend
   npm install
   npm start
   ```
   The frontend will be available at `http://localhost:3000`

3. **Monitor Face Detection Logs** (Optional)
   In a new terminal:
   ```bash
   cd backend
   python -m dev_loggers.monitor_face_detection
   ```
   You should see:
   ```
   === WhisperWell Face Detection Monitor ===
   Monitoring facial expressions and emotions in real-time
   Press Ctrl+C to exit
   =============================================
   ```
   
   When using the webcam, you'll see emotion detection logs like:
   ```
   2025-02-28 11:01:31 😊 EMOTION DETECTED:
     Primary: HAPPY (85.0%)
     Detailed Scores:
       happy      85.0% |████████████████
       neutral    10.0% |██
       sad         2.0% |
   ```

   **Note:** 
   - Face detection logs only appear in this monitor window
   - The main application terminal stays clean
   - Press `Ctrl+C` to stop monitoring

## Development Tools

### Logging System

The application uses a dedicated logging system for different components:

- **Main Application Logs**: Shown in the main terminal
- **Face Detection Logs**: Available in a separate monitoring window
- Log files are stored in `backend/logs/`

### Directory Structure
