# Runbooks · day 2

The TypeScript workshop uses Flue for the agent loop. This Python project keeps the same notes bot and calls Claude from `src/chat.py`.

| Step | Topic |
|---|---|
| 00 | Setup: Python, Anthropic key, Telegram bot |
| 01 | One conversation with Claude |
| 02 | Telegram: one history per chat id |
| 03 | saveNote and searchNotes |
| 04 | deleteNotes only for OWNER_CHAT_ID |
| 05 | Log tool names and token counts |
| 06 | Standup skill: description first, full text after activate_skill |

Start at [00. Setup](00-setup.md). The finished code is the current `src/` tree.
