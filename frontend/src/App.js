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
  // Core state
  const [messages, setMessages] = useState([
    { message: "Hey, I'm Nina, I'm here to listen to whatever is on your mind!", sender: "bot" },
  ]);
  
  // UI state
  const [isTyping, setIsTyping] = useState(false);
  const [isResponding, setIsResponding] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Character & image state
  const [currentCharacter, setCurrentCharacter] = useState('nina');
  const [currImage, setCurrImage] = useState(ninaImage);
  const [imageKey, setImageKey] = useState(0);
  
  // Settings
  const [voiceEnabled, setVoiceEnabled] = useState(false);

  // Welcome messages for each character
  const welcomeMessages = {
    nina: "Hey, I'm Nina, I'm here to listen to whatever is on your mind!",
    harold: "Hello there, I'm Harold. With my decades of experience, I'm here to help you find practical solutions to life's challenges."
  };

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
    
    try {
      // Send to backend
      const response = await fetch('http://127.0.0.1:5001/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          sessionId: 'default',
          voiceEnabled,
          character: currentCharacter
        })
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
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
      console.error("Error:", error);
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
    setCurrImage(characterId === 'nina' ? ninaImage : haroldImage);
    
    // Reset chat with appropriate welcome message
    setMessages([
      { message: welcomeMessages[characterId], sender: "bot" }
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
        onModelChange={(model) => console.log(`Switched to ${model} model`)}
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
                    (currentCharacter === "nina" ? "Nina" : "Harold") : "You"} 
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
