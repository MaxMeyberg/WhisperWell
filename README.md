# Talk2Me: AI Therapy Solution 🤖

An affordable AI therapy solution providing on-demand crisis support, emotional expression, and preliminary mental health insights.

## Quick Start Guide (Copy-Paste Friendly)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/winsonc7/CS224G.git

# Navigate to project folder
cd CS224G

# Create .env file
touch .env
```

### 2. Add Your API Keys
Copy this into your `.env` file and replace the xxxxx with your API keys:
```
OPENAI_API_KEY=xxxxx
ANTHROPIC_API_KEY=xxxxx
ELEVENLABS_API_KEY=xxxxx
ELEVENLABS_VOICE_ID=xxxxx
BLACK_FOREST_API_KEY=xxxxx
```

Get your API keys here:
- OpenAI API key: https://platform.openai.com/api-keys
- Anthropic API key: https://console.anthropic.com/
- ElevenLabs API key: https://elevenlabs.io/
- Black Forest Labs API key: https://www.blackforestlabs.com/

### 3. Install Dependencies

```bash
# Install Python packages
pip install flask flask-cors python-dotenv openai anthropic requests

# Navigate to frontend
cd frontend

# Install frontend packages
npm install

# Go back to root directory
cd ..
```

### 4. Run the Application

Open two terminal windows and run these commands:

Terminal 1 (Backend):
```bash
python backend/app.py
```

Terminal 2 (Frontend):
```bash
cd frontend
npm start
```

The app will open automatically at http://localhost:3000

### 5. Start Chatting!
- Use the toggle in the UI to switch between GPT-4 and Claude 3.5
- Enable/disable voice responses with the voice toggle
- Start chatting with Nina!

## Features 🌟
- 🤖 Choice between GPT-4 and Claude 3.5 AI models
- 🗣️ Voice toggle for audio responses
- 😊 Dynamic emotional responses with image generation
- 📝 Real-time conversation analysis
- 💭 Crisis support and emotional guidance
- 🎯 Professional boundary maintenance

## Development 👩‍💻

Info on general sprint progress and individual contributions are in the `progress` folder.

[Link to Sprint 2 progress and contributions](https://github.com/winsonc7/CS224G/blob/main/progress/SPRINT_TWO.md)

# Run our Multimodal Agent Prototype ⚙️:

We experiment with new prompts, features, etc. using our terminal prototype in the `prototype` folder. Our latest experiments feature
voice therapy solutions using ElevenLabs APIs.

(Aside: Chat with our voice agent directly in the browser [here](https://elevenlabs.io/app/talk-to?agent_id=aB08fUqZnmePxNvmkWTM))

To run the agent, make sure you're in the root directory and run:
```bash
poetry run python prototype/run.py
```
From then on, follow the instructions in the terminal. Press Ctrl+C or type 'exit' to quit.

**[FEATURE TODD IN FUTURE] Note: When testing voice features, use headphones to prevent audio feedback.**

---
# Developer Culture 🔧
- If you're working on a task, create an issue for it and assign it to yourself. Write updates as comments on your issue until you complete your task, upon which you can close your issue.
- If you're writing new code, create a branch with the naming format "FIRSTNAME-BRANCH-REASON" (for example, winson-cot-prompts).
- The main branch should ideally never have any bugs, and represents our overall progress. **Commits should only be pushed to main in the cases of (1) minor bug fixes or (2) markdown file updates.**
- When you want to merge your changes to main, submit a pull request and have another team member review your code prior to completing the merge. For cleanliness, make sure to delete your branch after it's been merged.

## Features


### Project Progress
Check the `progress` folder for sprint updates and contributions.
[Sprint 2 Progress](https://github.com/winsonc7/CS224G/blob/main/progress/SPRINT_TWO.md)
