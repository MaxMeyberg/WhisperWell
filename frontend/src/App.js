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
  const [currImage, setCurrImage] = useState(ninaImage);
  const [imageKey, setImageKey] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [currentCharacter, setCurrentCharacter] = useState('nina');

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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          sessionId: 'default',
          voiceEnabled: voiceEnabled,
          character: currentCharacter
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Update image immediately when we get response
      if (data.therapistImage) {
        setCurrImage(data.therapistImage);
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

  const handleModelChange = (newModel) => {
    console.log(`Switched to ${newModel} model`);
    // You could update UI or state here
  };

  const handleCharacterChange = (characterId) => {
    setCurrentCharacter(characterId);
    // Update the displayed image based on selected character
    setCurrImage(characterId === 'nina' ? ninaImage : haroldImage);
    
    // Reset chat when character changes
    setMessages([
      { 
        message: characterId === 'nina' 
          ? "Hey, I'm Nina, I'm here to listen to whatever is on your mind!" 
          : "Hello there, I'm Harold. With my decades of experience, I'm here to help you find practical solutions to life's challenges.",
        sender: "bot" 
      },
    ]);
  };

  return (
    <div className="app-container">
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
        onModelChange={handleModelChange}
        currentCharacter={currentCharacter}
        onCharacterChange={handleCharacterChange}
      />

      <div className="image-box">
        <div className="therapist-image-frame">
          <img 
            key={imageKey}
            src={currImage} 
            alt="AI Therapist"
            className={`therapist-image ${isImageLoading ? 'loading' : ''}`}
            onLoad={handleImageLoad}
          />
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
                  <Message.Header sender={msg.sender === "bot" ? currentCharacter === "nina" ? "Nina" : "Harold" : "You"} />
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
