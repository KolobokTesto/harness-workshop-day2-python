import json
import os
import sys
import urllib.request

import anthropic

MODEL = (os.environ.get("ANTHROPIC_MODEL") or "claude-haiku-4-5")


def check_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN порожній. Візьми токен у @BotFather і встав у .env.")
    url = f"https://api.telegram.org/bot{token}/getMe"
    with urllib.request.urlopen(url, timeout=30) as response:
        data = json.loads(response.read().decode())
    if not data.get("ok"):
        raise RuntimeError(f"Telegram не прийняв токен: {data.get('description')}")
    print(f"Telegram: бот @{data['result']['username']} на зв'язку.")


def check_model():
    key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY порожній.")
    client = anthropic.Anthropic(api_key=key, max_retries=0)
    reply = client.messages.create(
        model=MODEL,
        max_tokens=128,
        timeout=60,
        tools=[{"name": "ready", "description": "Connection check. Has no side effects.", "input_schema": {"type": "object", "properties": {}}}],
        tool_choice={"type": "tool", "name": "ready"},
        messages=[{"role": "user", "content": "Call the ready tool once."}],
    )
    if not any(getattr(block, "type", None) == "tool_use" and block.name == "ready" for block in reply.content):
        raise RuntimeError("Модель відповіла, але не викликала тул.")
    print(f"Модель {MODEL}: ключ працює, тул викликано.")


def main():
    ok = True
    for check in (check_telegram, check_model):
        try:
            check()
        except Exception as error:
            ok = False
            print("Не пройшло:", error, file=sys.stderr)
    if ok:
        print("Усе готово до практики.")
    else:
        print("Перевір .env.", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
