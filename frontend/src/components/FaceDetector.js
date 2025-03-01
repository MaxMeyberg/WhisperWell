import React, { useRef, useEffect, useState, useCallback } from 'react';

const FaceDetector = ({ onFaceUpdate, isEnabled }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isActive, setIsActive] = useState(false);

  // Define functions first, before they're used in useEffect
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 320, height: 240 } 
      });
      videoRef.current.srcObject = stream;
      // Add event listener to verify video is playing
      videoRef.current.onloadedmetadata = () => {
        console.log("Video stream started");
        videoRef.current.play();
      };
      videoRef.current.onplay = () => {
        console.log("Video is playing");
      };
      setIsActive(true);
    } catch (err) {
      console.error("Error accessing webcam:", err.name, err.message);
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsActive(false);
    if (onFaceUpdate) onFaceUpdate(null);
  }, [onFaceUpdate]);

  const detectFace = useCallback(async () => {
    if (!isActive || !videoRef.current || !canvasRef.current) return;
    
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      // Add timestamp to verify new frames
      const timestamp = new Date().toISOString();
      console.log(`Capturing new frame at: ${timestamp}`);
      
      // Capture frame from video
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      console.log("Video ready state:", video.readyState);
      console.log("Video dimensions:", video.videoWidth, "x", video.videoHeight);
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Get image data to verify it's not black
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      const pixels = imageData.data;
      const isBlack = pixels.every((val, i) => i % 4 === 3 || val === 0);
      console.log("Frame is all black:", isBlack);
      
      // Log image dimensions
      console.log("Face detection dimensions:", canvas.width, canvas.height);
      
      // Convert to base64
      const imageDataBase64 = canvas.toDataURL('image/jpeg', 0.7);
      // Log the first 100 characters of image data to verify it's not empty
      console.log("Image data preview:", imageDataBase64.substring(0, 100));
      console.log("Image data length:", imageDataBase64.length);
      
      console.log("Sending face detection request...");
      const response = await fetch('http://127.0.0.1:5001/api/detect_face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageDataBase64 })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log("Face detection response:", data);
        if (onFaceUpdate) onFaceUpdate(data);
      }
    } catch (error) {
      console.error("Face detection error details:", error);
      // If the error persists, pause face detection
      if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
        console.log("Backend server may be down, pausing face detection");
        setIsActive(false);
      }
    }
  }, [isActive, videoRef, canvasRef, onFaceUpdate]);

  // Now use the functions in useEffect
  useEffect(() => {
    if (isEnabled && !isActive) {
      startCamera();
    } else if (!isEnabled && isActive) {
      stopCamera();
    }
  }, [isEnabled, isActive, startCamera, stopCamera]);

  // Detect face on interval when camera is active
  useEffect(() => {
    let timerId;
    if (isActive) {
      // Run face detection every 3 seconds
      timerId = setInterval(detectFace, 3000);
    }
    
    return () => {
      if (timerId) clearInterval(timerId);
    };
  }, [isActive, detectFace]);

  return (
    <div className="face-detector" style={{ display: 'none' }}>
      <div className="webcam-container">
        <video 
          ref={videoRef} 
          autoPlay 
          muted 
          className="webcam-video"
          style={{ 
            position: 'fixed',
            top: 0,
            left: 0,
            width: '160px',  // Small preview
            height: '120px',
            zIndex: 9999
          }}
        />
        <canvas 
          ref={canvasRef} 
          style={{ 
            position: 'absolute',
            visibility: 'hidden'  // Hide but keep active
          }}
        />
      </div>
    </div>
  );
};

export default FaceDetector; 