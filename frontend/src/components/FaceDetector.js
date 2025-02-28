import React, { useRef, useEffect, useState, useCallback } from 'react';

const FaceDetector = ({ onFaceUpdate, isEnabled }) => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isActive, setIsActive] = useState(false);
  const [, setDetectedFace] = useState(null);

  // Define functions first, before they're used in useEffect
  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 320, height: 240 } 
      });
      videoRef.current.srcObject = stream;
      setIsActive(true);
    } catch (err) {
      console.error("Error accessing webcam:", err);
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
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    // Capture frame from video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg', 0.7);
    
    try {
      // Send to backend for analysis
      const response = await fetch('http://127.0.0.1:5001/api/detect_face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
      });
      
      if (response.ok) {
        const data = await response.json();
        if (onFaceUpdate) onFaceUpdate(data);
      }
    } catch (error) {
      console.error("Error detecting face:", error);
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
          style={{ display: 'none' }}
        />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>
    </div>
  );
};

export default FaceDetector; 