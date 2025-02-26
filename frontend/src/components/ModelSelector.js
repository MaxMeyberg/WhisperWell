import React from 'react';

const ModelSelector = ({ onModelChange }) => {
    const models = [
        { id: "ultra", name: "Ultra Quality" },
        { id: "standard", name: "Standard" },
        { id: "fast", name: "Fast Generation" },
        { id: "anime", name: "Anime Style" }
    ];

    const handleModelChange = async (modelType) => {
        try {
            const response = await fetch('http://localhost:5001/api/set_model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ model: modelType })
            });
            
            if (response.ok) {
                onModelChange(modelType);
            }
        } catch (error) {
            console.error('Failed to change model:', error);
        }
    };

    return (
        <div className="model-selector">
            <label>Image Style:</label>
            <select onChange={(e) => handleModelChange(e.target.value)}>
                {models.map(model => (
                    <option key={model.id} value={model.id}>
                        {model.name}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default ModelSelector; 