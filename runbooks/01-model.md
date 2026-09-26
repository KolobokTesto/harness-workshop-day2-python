# 01. Model

## What and why

Send one user message and print Claude's reply. The system prompt says the assistant replies in Ukrainian and must not invent saved notes. Tests use a scripted model, so this step does not need the network. The same chat id keeps earlier messages. A different id starts empty.

## Check

```bash
pytest -k "01"
python -m src.ask "Привіт"
```

## Ready code

`ask_agent` appends the user text, calls `messages.create`, and returns the text. An empty model reply raises `Модель не повернула текст.` The default model id is `claude-haiku-4-5`.
