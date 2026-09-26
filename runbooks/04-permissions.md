# 04. Permissions

## What and why

`deleteNotes` is offered only when the chat id equals `OWNER_CHAT_ID`. An empty owner id means nobody is the owner. If some other chat asks the model to delete, the tool is missing. A direct call still returns `not found` and does not change the file. The owner delete removes only that chat's notes.

## Check

```bash
pytest -k "04"
```

Set `OWNER_CHAT_ID` to the id printed by `/start` before running the live bot.

## Ready code

`is_owner` in `src/settings.py` is read by the loop when it builds the tool list. The value is not copied into the system prompt.
