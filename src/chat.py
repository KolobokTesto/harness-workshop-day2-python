import json

from src.claude_model import ClaudeModel, tool_result_message
from src.tools import SYSTEM, run_tool, tool_specs

MAX_STEPS = 8
conversations = {}


def reset_conversations():
    conversations.clear()


def ask_agent(chat_id, text, model=None):
    model = model or ClaudeModel()
    history = conversations.setdefault(chat_id, [])
    history.append({"role": "user", "content": text})
    include_delete = False
    for _step in range(MAX_STEPS):
        tools = tool_specs(include_delete)
        reply = model.generate(system=SYSTEM, messages=history, tools=tools)
        if not reply["tool_calls"]:
            if not reply["text"].strip():
                raise RuntimeError("Модель не повернула текст.")
            history.append({"role": "assistant", "content": reply["content"] or reply["text"]})
            return reply["text"]
        history.append({"role": "assistant", "content": reply["content"]})
        pairs = []
        logged = []
        for call in reply["tool_calls"]:
            try:
                result = run_tool(chat_id, call["name"], call["input"], include_delete)
            except Exception as error:
                result = {"isError": True, "error": str(error)}
            pairs.append((call, result))
            logged.append({"tool": call["name"], "isError": bool(result.get("isError"))})
        history.append(tool_result_message(pairs))
    raise RuntimeError("Досягли ліміту кроків.")
