/**
 * @fileoverview Main React component for the Talk2Me therapy chatbot application.
 * This component implements a chat interface using the chatscope UI kit,
 * providing real-time interaction with the therapy chatbot.
 */

import React, { useState } from "react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
  ConversationHeader,
} from "@chatscope/chat-ui-kit-react";
import "./App.css";
import ninaImage from './assets/Nina.png';
import haroldImage from './assets/Harold.png';
import SettingsMenu from './components/SettingsMenu';
import FaceDetector from './components/FaceDetector';

/**
 * Main application component that renders the chat interface
 * and handles message exchange with the backend server.
 * 
 * @component
 * @returns {JSX.Element} The rendered chat interface
 */
function App() {
  // Core state
  const [messages, setMessages] = useState([
    { message: "Hey, I'm Nina, I'm here to listen to whatever is on your mind!", sender: "bot" },
  ]);
  
  // UI state
  const [isTyping, setIsTyping] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Character & image state
  const [currentCharacter, setCurrentCharacter] = useState('Nina');
  const [currImage, setCurrImage] = useState(ninaImage);
  const [imageKey, setImageKey] = useState(0);
  
  // Settings
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [faceEnabled, setFaceEnabled] = useState(false);
  const [userFace, setUserFace] = useState(null);
  const [CurrFLUXModel, setCurrFLUXModel] = useState('standard');

  // Welcome messages for each character
  const welcomeMessages = {
    Nina: "Hey, I'm Nina, I'm here to listen to whatever is on your mind!",
    Harold: "Hello there, I'm Harold. With my decades of experience, I'm here to help you find practical solutions to life's challenges."
  };

  // Add this to your state variables
  const [captureCounter, setCaptureCounter] = useState(0);

  /**
   * Handles sending messages to the backend server and updating the chat UI.
   * 
   * @param {string} text - The message text to send
   * @returns {Promise<void>}
   */
  const handleSend = async (text) => {
    // Skip if already responding or empty message
    if (isResponding || !text.trim()) return;
    
    // Add user message to chat
    const newMessage = { message: text, sender: "user", timestamp: new Date() };
    setMessages([...messages, newMessage]);
    
    // Set loading states
    setIsResponding(true);
    setIsTyping(true);
    
    // Trigger face capture if enabled
    if (faceEnabled) {
      setCaptureCounter(prev => prev + 1);
    }
    
    // Wait a moment for face capture to complete
    if (faceEnabled) {
      await new Promise(resolve => setTimeout(resolve, 300));
    }
    
    try {
      // Capture face if enabled
      let currentFace = userFace;
      
      // Send to backend
      const response = await fetch('http://localhost:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          sessionId: 'default',
          voiceEnabled,
          character: currentCharacter,
          userFace: faceEnabled ? currentFace : null,
          model: CurrFLUXModel
        })
      });

      // Add better error handling
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Server error: ${response.status}`, errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      
      // Update therapist image
      if (data.therapistImage) {
        setCurrImage(data.therapistImage);
        setImageKey(prev => prev + 1);
      }

      // Handle audio if enabled
      if (data.audioData) {
        playAudio(data.audioData);
      } else {
        setIsResponding(false);
      }

      // Add bot message
      setMessages(prev => [
        ...prev,
        { message: data.message, sender: "bot", timestamp: new Date() }
      ]);
      
    } catch (error) {
      console.error("Error details:", error);
      // Show error to user
      setMessages(prev => [
        ...prev,
        { message: "Sorry, I'm having trouble connecting. Please try again.", sender: "bot", timestamp: new Date() }
      ]);
      setIsResponding(false);
    } finally {
      setIsTyping(false);
    }
  };

  // Helper to play audio data
  const playAudio = (audioData) => {
    const audioBlob = new Blob(
      [Uint8Array.from(atob(audioData), c => c.charCodeAt(0))],
      { type: 'audio/mpeg' }
    );
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    audio.play().catch(e => console.error("Audio playback error:", e));
    
    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      setIsResponding(false);
    };
  };

  const handleCharacterChange = (characterId) => {
    setCurrentCharacter(characterId);
    setCurrImage(characterId === 'Nina' ? ninaImage : haroldImage);
    
    // Reset chat with appropriate welcome message
    setMessages([
      { message: welcomeMessages[characterId], sender: "bot" }
    ]);
  };

  return (
    <div className="app-container">
      {/* Face detector is now hidden */}
      <FaceDetector 
        onFaceUpdate={setUserFace} 
        isEnabled={faceEnabled} 
      />
      
      {/* Settings Button */}
      <button 
        className="settings-button"
        onClick={() => setIsSettingsOpen(true)}
      >
        ⚙️
      </button>

      {/* Settings Menu */}
      <SettingsMenu
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        voiceEnabled={voiceEnabled}
        onVoiceToggle={() => setVoiceEnabled(!voiceEnabled)}
        faceEnabled={faceEnabled}
        onFaceToggle={() => setFaceEnabled(!faceEnabled)}
        FLUXModel={CurrFLUXModel}
        onModelChange={(model) => setCurrFLUXModel(model)}
        currentCharacter={currentCharacter}
        onCharacterChange={handleCharacterChange}
      />

      <div className="image-box">
        <img 
          key={imageKey}
          src={currImage} 
          alt="AI Therapist"
          className="therapist-image"
        />
      </div>
      
      <div className="chat-window">
        <MainContainer>
          <ChatContainer>
            <ConversationHeader>
              <ConversationHeader.Content userName="Emotion Well" />
            </ConversationHeader>
            
            <MessageList 
              typingIndicator={isTyping ? <TypingIndicator content="Lemme think this through..." /> : null}
            >
              {messages.map((msg, i) => (
                <Message 
                  key={i}
                  model={{
                    message: msg.message,
                    sender: msg.sender,
                    direction: msg.sender === "user" ? "outgoing" : "incoming",
                    position: "single"
                  }}
                >
                  <Message.Header sender={msg.sender === "bot" ? 
                    (currentCharacter === "Nina" ? "Nina" : "Harold") : "You"} 
                  />
                </Message>
              ))}
            </MessageList>
            
            <MessageInput 
              placeholder="Type your message here..."
              onSend={handleSend}
              attachButton={false}
              disabled={isResponding}
            />
          </ChatContainer>
        </MainContainer>
      </div>
      
      {isResponding && (
        <div className="nina-typing-indicator">
          <span>...</span>
        </div>
      )}
    </div>
  );
}

export default App;
