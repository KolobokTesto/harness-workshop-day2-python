# Harness Workshop Python · day 2

Yesterday's agent kept its own loop. Today the same notes assistant lives in Telegram. There is no Python port of Flue, so this project keeps that behavior in `src/chat.py`: one conversation per chat id, tool execution, and a scripted model in tests. The model is Claude.

The bot remembers notes, searches them, deletes them only for the owner, and can draft a standup from the standup skill.

## Setup

```bash
cd harness-workshop-day2-python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill `ANTHROPIC_API_KEY` and `TELEGRAM_BOT_TOKEN`. Create the bot with @BotFather.

## Commands

```bash
python -m src.ask "Запам'ятай купити молоко"
python -m src.bot
python scripts/check_setup.py
pytest
```

`notes.json` and `.env` stay out of git. See `runbooks/README.md`.
