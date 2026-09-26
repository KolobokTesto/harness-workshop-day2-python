from pydantic import BaseModel, Field, field_validator

from src.notes import MAX_NOTE_CHARACTERS, delete_notes, save_note, search_notes
from src.skill import STANDUP

SYSTEM = "\n".join(
    [
        "You are a personal notes assistant in Telegram. Reply in Ukrainian, briefly.",
        "Use saveNote and searchNotes for notes. Never claim a note is saved or found without a tool result.",
        "If a tool returns an error, tell the user what failed.",
        f"Skills: {STANDUP['name']}: {STANDUP['description']}. Call activate_skill with that name before following it.",
    ]
)


class SaveInput(BaseModel):
    text: str = Field(min_length=1, max_length=MAX_NOTE_CHARACTERS)

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class SearchInput(BaseModel):
    query: str = ""


def tool_specs(include_delete):
    specs = [
        {
            "name": "saveNote",
            "description": "Save one note for the user when they ask to remember something.",
            "input_schema": SaveInput.model_json_schema(),
        },
        {
            "name": "searchNotes",
            "description": "Find the user's saved notes that contain the query. An empty query returns all notes with their dates.",
            "input_schema": SearchInput.model_json_schema(),
        },
        {
            "name": "activate_skill",
            "description": f"Load the full instructions for a skill. Available: {STANDUP['name']}.",
            "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]},
        },
    ]
    if include_delete:
        specs.append(
            {
                "name": "deleteNotes",
                "description": "Delete all of the user's notes. Use only when the user explicitly asks to delete them.",
                "input_schema": {"type": "object", "properties": {}},
            }
        )
    return specs


def run_tool(chat_id, name, tool_input, include_delete):
    if name == "saveNote":
        data = SaveInput.model_validate(tool_input)
        return {"isError": False, "output": save_note(chat_id, data.text)}
    if name == "searchNotes":
        data = SearchInput.model_validate(tool_input or {})
        return {"isError": False, "output": search_notes(chat_id, data.query)}
    if name == "activate_skill":
        if (tool_input or {}).get("name") != STANDUP["name"]:
            return {"isError": True, "error": "not found"}
        return {"isError": False, "output": STANDUP["instructions"]}
    if name == "deleteNotes":
        if not include_delete:
            return {"isError": True, "error": "not found"}
        return {"isError": False, "output": delete_notes(chat_id)}
    return {"isError": True, "error": "not found"}
