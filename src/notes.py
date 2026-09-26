import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

MAX_NOTE_CHARACTERS = 2_000


def notes_file():
    return os.environ.get("NOTES_FILE") or "notes.json"


def read_notes():
    path = Path(notes_file())
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def write_notes(notes):
    Path(notes_file()).write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")


def save_note(chat_id, text):
    note = {
        "id": str(uuid.uuid4()),
        "chatId": chat_id,
        "text": text.strip(),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    write_notes([*read_notes(), note])
    return note


def search_notes(chat_id, query=""):
    search = query.strip().lower()
    return [
        note
        for note in read_notes()
        if note["chatId"] == chat_id and search in note["text"].lower()
    ]


def delete_notes(chat_id):
    notes = read_notes()
    remaining = [note for note in notes if note["chatId"] != chat_id]
    write_notes(remaining)
    return {"deleted": len(notes) - len(remaining)}
