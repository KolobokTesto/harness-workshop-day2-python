# 06. Skill

## What and why

The standup skill is a markdown file. The system prompt lists its name and description only. `activate_skill` returns the body, with the front matter removed. The model should call it before writing a standup, then `searchNotes` with an empty query, and must not invent facts.

## Check

```bash
pytest -k "06"
```

## Ready code

`skills/standup/SKILL.md` holds the instructions. `src/skill.py` reads the description. The tool result is the only place the sentence `Не вигадуй фактів` appears.
