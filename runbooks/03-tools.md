# 03. Tools

## What and why

Notes live in `notes.json`. `saveNote` and `searchNotes` receive the chat id from our code, not from the model, so one chat cannot read another chat's notes. Empty or whitespace text fails validation and comes back as a tool error. The model sees that error on the next request and should tell the user.

## Check

```bash
pytest -k "03"
```

## Ready code

`src/notes.py` filters by `chatId`. `src/tools.py` validates with Pydantic. `src/chat.py` runs the tool and appends a `tool_result` before asking Claude again.
