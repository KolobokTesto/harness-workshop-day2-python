import json
import os

import anthropic

DEFAULT_MODEL = "claude-haiku-4-5"
MAX_OUTPUT_TOKENS = 512


class ClaudeModel:
    def __init__(self, client=None):
        model = os.environ.get("ANTHROPIC_MODEL") or os.environ.get("MODEL") or DEFAULT_MODEL
        self.model_id = model.split("/", 1)[-1]
        self.client = client or anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY") or "missing",
            max_retries=0,
        )

    def generate(self, *, system, messages, tools):
        message = self.client.messages.create(
            model=self.model_id,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=system,
            messages=messages,
            tools=tools or anthropic.NOT_GIVEN,
            timeout=60,
        )
        return _reply(message)


def _reply(message):
    texts = []
    calls = []
    content = []
    for block in message.content:
        if block.type == "text":
            texts.append(block.text)
            content.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            calls.append({"id": block.id, "name": block.name, "input": block.input})
            content.append({"type": "tool_use", "id": block.id, "name": block.name, "input": block.input})
    usage = getattr(message, "usage", None)
    total = 0
    if usage is not None:
        total = getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)
    return {
        "text": "".join(texts),
        "tool_calls": calls,
        "content": content,
        "totalTokens": total,
    }


def tool_result_message(calls_and_results):
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": call["id"],
                "content": json.dumps(result, ensure_ascii=False),
            }
            for call, result in calls_and_results
        ],
    }
