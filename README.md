# 🎙️ Transcription Bot

Telegram bot that automatically transcribes voice messages, audio files, and video notes in group chats using AssemblyAI. Supports 99 languages.

## Features

- Handles voice messages, audio files, and video notes (circles)
- Auto language detection
- Deployable (e.g. on Railway free tier for me)

## Setup

### 1. Clone

```bash
git clone https://github.com/stacyshki/InGroupTranscriptionBot.git
cd InGroupTranscriptionBot
```

### 2. Environment variables

Copy `.env.example` to `.env` and fill in:

```
TG_TOKEN=your_telegram_bot_token
ASSEMBLYAI_KEY=your_assemblyai_api_key
```

Get tokens:

- Telegram: [@BotFather](https://t.me/BotFather) → `/newbot`
- AssemblyAI: [assemblyai.com](https://www.assemblyai.com) → Dashboard → API key

### 3. Run locally

```bash
pip install -r requirements.txt
python app.py
```

## Deploy on Railway

1. Push to GitHub
2. New Project → Deploy from GitHub repo
3. Add `TELEGRAM_TOKEN` and `ASSEMBLY_AI_KEY` in Variables tab
4. Railway will pick up the `Procfile` automatically

## Bot setup in Telegram

1. [@BotFather](https://t.me/BotFather) → `/setprivacy` → select your bot → `Disable`  
   Required so the bot can see messages in group chats.
2. Add the bot to your group.

## Project structure

```
.
├── app.py
├── requirements.txt
├── Procfile
└── .env.example
```
