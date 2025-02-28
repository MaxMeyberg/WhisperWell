import React from 'react';
import './SettingsMenu.css';

const SettingsMenu = ({ isOpen, onClose, voiceEnabled, onVoiceToggle, faceEnabled, onFaceToggle, onModelChange, currentCharacter, onCharacterChange }) => {
    const models = [
        { id: "ultra", name: "Ultra" },
        { id: "standard", name: "Standard" },
        { id: "fast", name: "Fast" },
        { id: "anime", name: "Anime" }
    ];
    
    const characters = [
        { id: "nina", name: "Nina (Young Therapist)" },
        { id: "harold", name: "Harold (Wise Elder)" }
    ];

    return (
        <>
            {/* Backdrop */}
            {isOpen && <div className="settings-backdrop" onClick={onClose} />}
            
            {/* Settings Panel */}
            <div className={`settings-menu ${isOpen ? 'open' : ''}`}>
                <div className="settings-header">
                    <h3>Settings</h3>
                    <button className="close-button" onClick={onClose}>×</button>
                </div>
                
                <div className="settings-content">
                    {/* Character Selection */}
                    <div className="setting-item">
                        <span>Character</span>
                        <select 
                            value={currentCharacter} 
                            onChange={(e) => onCharacterChange(e.target.value)}
                        >
                            {characters.map(char => (
                                <option key={char.id} value={char.id}>
                                    {char.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Voice Toggle */}
                    <div className="setting-item">
                        <span>Voice Mode</span>
                        <label className="switch">
                            <input 
                                type="checkbox" 
                                checked={voiceEnabled} 
                                onChange={onVoiceToggle}
                            />
                            <span className="slider round"></span>
                        </label>
                    </div>

                    {/* Face Toggle */}
                    <div className="setting-item">
                        <span>Face Recognition</span>
                        <label className="switch">
                            <input 
                                type="checkbox" 
                                checked={faceEnabled} 
                                onChange={onFaceToggle}
                            />
                            <span className="slider round"></span>
                        </label>
                    </div>

                    {/* Model Selector */}
                    <div className="setting-item">
                        <span>Image Quality</span>
                        <select onChange={(e) => onModelChange(e.target.value)}>
                            {models.map(model => (
                                <option key={model.id} value={model.id}>
                                    {model.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
        </>
    );
};

export default SettingsMenu; 