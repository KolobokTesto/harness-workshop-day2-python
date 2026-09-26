# 05. Feedback

## What and why

After each model turn the process prints one JSON line: which tools ran and how many tokens the call used. A failed tool is marked `(помилка)`. The line does not include the user's message, so secrets from the chat stay out of that log.

## Check

```bash
pytest -k "05"
```

## Ready code

`log_response` in `src/log.py` prints `{"tools": [...], "totalTokens": N}`. `ask_agent` calls it after every Claude response, including the turn that only ran tools.
