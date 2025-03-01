import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

def setup_loggers():
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Silence Werkzeug logs
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)  # Only show warnings and errors
    
    # Console handler for main application logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Configure camera service logger with file output
    camera_logger = logging.getLogger('camera_service')
    camera_logger.setLevel(logging.INFO)
    camera_logger.propagate = False  # Don't send logs to console
    
    # File handler for camera service logs
    file_handler = RotatingFileHandler(
        'logs/face_detection.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    camera_logger.addHandler(file_handler)
    
    # Remove any existing console handlers from camera logger
    for handler in camera_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            camera_logger.removeHandler(handler)
    
    return root_logger, camera_logger 