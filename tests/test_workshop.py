import importlib
import json
from pathlib import Path

import pytest


def ask_agent(*args, **kwargs):
    if importlib.util.find_spec("src.chat") is not None:
        from src.chat import ask_agent as fn
    else:
        from src.agent import ask_agent as fn
    return fn(*args, **kwargs)


def reset_conversations():
    if importlib.util.find_spec("src.chat") is not None:
        from src.chat import reset_conversations as fn
    elif importlib.util.find_spec("src.agent") is not None:
        from src.agent import reset_conversations as fn
    else:
        return
    fn()


class ScriptModel:
    def __init__(self, steps):
        self.steps = list(steps)
        self.requests = []

    def generate(self, *, system, messages, tools):
        self.requests.append({"systemPrompt": system, "messages": messages, "tools": tools})
        step = self.steps.pop(0)
        if "tool" in step:
            return {
                "text": "",
                "tool_calls": [{"id": "call", "name": step["tool"], "input": step["input"]}],
                "content": [{"type": "tool_use", "id": "call", "name": step["tool"], "input": step["input"]}],
                "totalTokens": 12,
            }
        return {
            "text": step["text"],
            "tool_calls": [],
            "content": [{"type": "text", "text": step["text"]}],
            "totalTokens": 8,
        }


def tool_names(model, index=-1):
    service = {"activate_skill"}
    return [tool["name"] for tool in model.requests[index]["tools"] if tool["name"] not in service]


def messages_text(model, index=-1):
    return json.dumps(model.requests[index]["messages"], ensure_ascii=False)


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    reset_conversations()
    monkeypatch.delenv("OWNER_CHAT_ID", raising=False)
    yield
    reset_conversations()


def test_00_runbooks_exist():
    root = Path(__file__).resolve().parent.parent / "runbooks"
    names = ["README", "00-setup", "01-model", "02-telegram", "03-tools", "04-permissions", "05-feedback", "06-skill"]
    for name in names:
        text = (root / f"{name}.md").read_text(encoding="utf-8")
        assert len(text) > 200, name


@pytest.mark.step(1)
def test_01_agent_returns_model_text():
    model = ScriptModel([{"text": "Привіт!"}])
    assert ask_agent("agent-1", "Привіт", model) == "Привіт!"
    assert "Ukrainian" in model.requests[0]["systemPrompt"]


@pytest.mark.step(1)
def test_01_memory_is_per_chat():
    model = ScriptModel([{"text": "Запам'ятав."}, {"text": "Тебе звати Оля."}, {"text": "Не знаю."}])
    ask_agent("memory-1", "Мене звати Оля", model)
    ask_agent("memory-1", "Як мене звати?", model)
    assert "Мене звати Оля" in messages_text(model, 1)
    ask_agent("memory-2", "Як мене звати?", model)
    assert "Оля" not in messages_text(model, 2)


@pytest.mark.step(2)
def test_02_ask_agent_separates_chats():
    model = ScriptModel([{"text": "Відповідь для 42"}, {"text": "Відповідь для 7"}])
    assert ask_agent("42", "Я з чату 42", model) == "Відповідь для 42"
    assert ask_agent("7", "Я з чату 7", model) == "Відповідь для 7"
    assert "чату 42" not in messages_text(model, 1)


@pytest.mark.step(2)
def test_02_empty_reply_is_an_error():
    model = ScriptModel([{"text": ""}])
    with pytest.raises(RuntimeError, match="не повернула текст"):
        ask_agent("empty", "Привіт", model)


@pytest.mark.step(3)
def test_03_notes_stay_in_their_chat(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    from src.notes import read_notes, save_note, search_notes
    assert read_notes() == []
    save_note("42", "  Зустріч із командою  ")
    save_note("7", "Зустріч із клієнтом")
    assert search_notes("42", "ЗУСТРІЧ")[0]["text"] == "Зустріч із командою"
    assert search_notes("42", "клієнтом") == []
    assert len(search_notes("42", "")) == 1


@pytest.mark.step(3)
def test_03_save_note_uses_chat_id_from_code(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    model = ScriptModel([
        {"tool": "saveNote", "input": {"text": "Купити молоко"}},
        {"text": "Зберіг."},
    ])
    assert ask_agent("42", "Запам'ятай: купити молоко", model) == "Зберіг."
    assert sorted(tool_names(model, 0)) == ["saveNote", "searchNotes"]
    notes = json.loads((tmp_path / "notes.json").read_text(encoding="utf-8"))
    assert notes[0]["chatId"] == "42"
    assert "Купити молоко" in messages_text(model, 1)


@pytest.mark.step(3)
def test_03_blank_text_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    model = ScriptModel([
        {"tool": "saveNote", "input": {"text": "   "}},
        {"text": "Не вийшло зберегти."},
    ])
    ask_agent("42", "Запам'ятай порожнє", model)
    from src.notes import read_notes
    assert read_notes() == []
    assert "isError" in messages_text(model, 1)


@pytest.mark.step(4)
def test_04_owner_flag(monkeypatch):
    from src.settings import is_owner
    monkeypatch.delenv("OWNER_CHAT_ID", raising=False)
    assert is_owner("42") is False
    monkeypatch.setenv("OWNER_CHAT_ID", "42")
    assert is_owner("42") is True
    assert is_owner("7") is False


@pytest.mark.step(4)
def test_04_delete_tool_only_for_owner(monkeypatch):
    monkeypatch.setenv("OWNER_CHAT_ID", "42")
    model = ScriptModel([{"text": "ok"}, {"text": "ok"}])
    ask_agent("7", "Привіт", model)
    ask_agent("42", "Привіт", model)
    assert "deleteNotes" not in tool_names(model, 0)
    assert "deleteNotes" in tool_names(model, 1)


@pytest.mark.step(4)
def test_04_stranger_cannot_delete(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    monkeypatch.setenv("OWNER_CHAT_ID", "42")
    from src.notes import read_notes, save_note
    save_note("42", "Моє")
    save_note("7", "Чуже")
    model = ScriptModel([
        {"tool": "deleteNotes", "input": {}},
        {"text": "Не можу."},
        {"tool": "deleteNotes", "input": {}},
        {"text": "Видалив."},
    ])
    ask_agent("7", "Видали все", model)
    assert len(read_notes()) == 2
    assert "not found" in messages_text(model, 1)
    ask_agent("42", "Видали мої нотатки", model)
    assert [note["chatId"] for note in read_notes()] == ["7"]


@pytest.mark.step(5)
def test_05_log_lists_tools_without_user_text(capsys, tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_FILE", str(tmp_path / "notes.json"))
    model = ScriptModel([
        {"tool": "saveNote", "input": {"text": "Секретний план"}},
        {"text": "Зберіг."},
    ])
    ask_agent("log-1", "Запам'ятай секретний план", model)
    line = next(text for text in capsys.readouterr().out.splitlines() if "totalTokens" in text)
    entry = json.loads(line)
    assert entry["tools"] == ["saveNote"]
    assert isinstance(entry["totalTokens"], int)
    assert "Секретний" not in line


@pytest.mark.step(6)
def test_06_skill_body_after_activate():
    from src.chat import conversations
    from src.skill import STANDUP
    from src.tools import SYSTEM
    assert not STANDUP["instructions"].startswith("---")
    model = ScriptModel([
        {"tool": "activate_skill", "input": {"name": "standup"}},
        {"text": "Вчора: …"},
    ])
    ask_agent("skill-1", "Зроби стендап", model)
    assert "standup" in model.requests[0]["systemPrompt"]
    assert "Не вигадуй фактів" not in model.requests[0]["systemPrompt"]
    assert "Не вигадуй фактів" in messages_text(model, 1)
    assert "Ukrainian" in SYSTEM
    assert conversations
