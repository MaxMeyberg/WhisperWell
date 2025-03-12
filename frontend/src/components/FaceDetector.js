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

  const captureAndSendImage = async () => {
    try {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext('2d').drawImage(video, 0, 0);
      
      // Get image as blob instead of base64
      canvas.toBlob(async (blob) => {
        // Create FormData
        const formData = new FormData();
        formData.append('image', blob, 'webcam.jpg');
        
        // Send to backend
        const response = await fetch('http://localhost:5001/api/read_face_portal', {
          method: 'POST',
          body: formData,  // No need to set Content-Type, browser sets it automatically
        });
        
        const data = await response.json();
        // Handle response as before
        if (onFaceUpdate) onFaceUpdate(data);
      }, 'image/jpeg');
    } catch (error) {
      console.error('Error capturing image:', error);
    }
  };

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
      // Run face detection every 0.5 seconds
      timerId = setInterval(captureAndSendImage, 500);
    }
    
    return () => {
      if (timerId) clearInterval(timerId);
    };
  }, [isActive, captureAndSendImage]);

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