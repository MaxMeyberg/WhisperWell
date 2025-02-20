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
import therapistSmile from './assets/therapist/Therapist-F-Smile.png';

/**
 * Main application component that renders the chat interface
 * and handles message exchange with the backend server.
 * 
 * @component
 * @returns {JSX.Element} The rendered chat interface
 */
function App() {
  const [messages, setMessages] = useState([
    { message: "Hey, I'm Nina, I'm here to listen to whatever is on your mind!", sender: "bot" },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isImageLoading, setIsImageLoading] = useState(false);
  const [currentTherapistImage, setCurrentTherapistImage] = useState(therapistSmile);
  const [currentAnimation, setCurrentAnimation] = useState(null);
  const [imageKey, setImageKey] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [selectedModel, setSelectedModel] = useState('gpt-3.5');
  const [isResponding, setIsResponding] = useState(false);

  /**
   * Handles sending messages to the backend server and updating the chat UI.
   * 
   * @param {string} text - The message text to send
   * @returns {Promise<void>}
   */
  const handleSend = async (text) => {
    if (isResponding) {
      return;
    }
    
    if (!text.trim()) return;

    const newMessage = { message: text, sender: "user", timestamp: new Date() };
    setMessages([...messages, newMessage]);
    
    setIsResponding(true);
    setIsTyping(true);
    setIsImageLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/chat', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: text,
          sessionId: 'default',
          voiceEnabled: voiceEnabled,
          model: selectedModel
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update image immediately when we get response
      if (data.therapistImage) {
        setCurrentTherapistImage(data.therapistImage);
        setImageKey(prev => prev + 1);
      }

      // Start audio immediately if voice is enabled
      if (data.audioData) {
        const audioBlob = new Blob(
          [Uint8Array.from(atob(data.audioData), c => c.charCodeAt(0))],
          { type: 'audio/mpeg' }
        );
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        // Play immediately
        audio.play().catch(e => console.error("Audio playback error:", e));
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setIsResponding(false);
        };
      }

      // Show Nina's message immediately
      setMessages(prev => [
        ...prev,
        { message: data.message, sender: "bot", timestamp: new Date() }
      ]);
      
      // If no voice, allow new messages immediately
      if (!voiceEnabled) {
        setIsResponding(false);
      }

    } catch (error) {
      console.error("Error:", error);
      setIsResponding(false);
    } finally {
      setIsTyping(false);
      setIsImageLoading(false);
    }
  };

  // Add image load handler
  const handleImageLoad = (e) => {
    console.log('New therapist image loaded:', {
      dimensions: {
        width: e.target.naturalWidth,
        height: e.target.naturalHeight
      },
      timestamp: new Date().toISOString()
    });
  };

  return (
    <div className="app-container">
      <div className="image-box">
        <div className="therapist-image-frame">
          {currentAnimation ? (
            <video 
              autoPlay 
              loop 
              muted 
              className="therapist-animation"
              src={currentAnimation}
            />
          ) : (
            <img 
              key={imageKey}
              src={currentTherapistImage} 
              alt="AI Therapist"
              className={`therapist-image ${isImageLoading ? 'loading' : ''}`}
              onLoad={handleImageLoad}
            />
          )}
        </div>
        <div className="controls-container">
          <div className="model-selector">
            <select 
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="model-select"
            >
              <option value="gpt-3.5">GPT-3.5</option>
              <option value="gpt-4">GPT-4</option>
              <option value="claude-3.5">Claude 3.5</option>
            </select>
          </div>
          <div className="voice-toggle">
            <label className="switch">
              <input
                type="checkbox"
                checked={voiceEnabled}
                onChange={(e) => setVoiceEnabled(e.target.checked)}
              />
              <span className="slider round"></span>
            </label>
            <span className="toggle-label">Voice {voiceEnabled ? 'On' : 'Off'}</span>
          </div>
        </div>
      </div>
      <div className="chat-window">
        <MainContainer>
          <ChatContainer>
            <ConversationHeader>
              <ConversationHeader.Content 
                userName="Talk2Me"
              />
            </ConversationHeader>
            <MessageList 
              typingIndicator={isTyping ? <TypingIndicator content="Lemme think this through..." /> : null}
              className="message-list"
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
                  <Message.Header sender={msg.sender === "bot" ? "Nina" : "You"} />
                </Message>
              ))}
            </MessageList>
            <MessageInput 
              placeholder="Type your message here..."
              onSend={handleSend}
              attachButton={false}
              className="message-input"
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
