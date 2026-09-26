import re
from pathlib import Path

TEXT = (Path(__file__).resolve().parent.parent / "skills" / "standup" / "SKILL.md").read_text(encoding="utf-8")
DESCRIPTION = re.search(r"^description: (.+)$", TEXT, re.M)
if not DESCRIPTION:
    raise RuntimeError("Немає description у skills/standup/SKILL.md")

STANDUP = {
    "name": "standup",
    "description": DESCRIPTION.group(1),
    "instructions": re.sub(r"^---[\s\S]*?---\s*", "", TEXT),
}
