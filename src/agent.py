conversations = {}

SYSTEM = """You are a personal notes assistant in Telegram. Reply in Ukrainian, briefly.
Say so when you do not know something."""


def reset_conversations():
    conversations.clear()


def ask_agent(chat_id, text, model=None):
    from src.claude_model import ClaudeModel
    model = model or ClaudeModel()
    history = conversations.setdefault(chat_id, [])
    history.append({"role": "user", "content": text})
    reply = model.generate(system=SYSTEM, messages=history, tools=[])
    if not reply["text"].strip():
        raise RuntimeError("Модель не повернула текст.")
    history.append({"role": "assistant", "content": reply["content"] or reply["text"]})
    return reply["text"]
