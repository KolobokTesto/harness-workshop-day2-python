# 02. Telegram

## What and why

`python -m src.bot` long-polls Telegram. `/start` replies with the numeric chat id. Every other text message goes to `ask_agent` with that id, so two people do not share a history. Replies longer than 4000 characters are split. A model or tool failure is printed in the terminal and the user sees a short apology.

## Check

```bash
python -m src.bot
```

Write to the bot from Telegram. Stop it with Ctrl+C.

## Ready code

`src/bot.py` uses `getUpdates` and `sendMessage`. `src/ask.py` is the same agent with the fixed id `terminal`, for a single message from the shell.
