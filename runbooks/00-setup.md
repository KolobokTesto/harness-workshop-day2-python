# 00. Setup

## What and why

Day 2 puts the notes assistant in Telegram. Install Python 3.11 or newer, create a virtualenv, and install `requirements.txt`. Create an Anthropic API key and a bot token with @BotFather. The model does not need a local download. The token lets Telegram deliver messages to this process.

Copy `.env.example` to `.env`. Set `ANTHROPIC_API_KEY`, leave `ANTHROPIC_MODEL=claude-haiku-4-5`, and set `TELEGRAM_BOT_TOKEN`. Leave `OWNER_CHAT_ID` empty until step 04, after the bot prints your chat id.

## Check

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/check_setup.py
```

## Ready code

The checker calls Telegram `getMe` and asks Claude to call a `ready` tool. Both must succeed before the workshop exercises.
