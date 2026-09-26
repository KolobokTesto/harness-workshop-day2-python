import json
import os
import sys
import urllib.request

from src.chat import ask_agent

TELEGRAM_LIMIT = 4_000


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Заповни TELEGRAM_BOT_TOKEN у .env.")
    me = _api(token, "getMe")
    print(f"Бот @{me['username']} запущений. Напиши йому в Telegram. Зупинити: Ctrl+C.")
    offset = 0
    while True:
        updates = _api(token, "getUpdates", {"timeout": 30, "offset": offset})
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            text = message.get("text") or ""
            if chat_id is None or not text:
                continue
            if text.startswith("/start"):
                print("Chat id:", chat_id)
                _send(token, chat_id, f"Привіт! Твій chat id: {chat_id}")
                continue
            try:
                answer = ask_agent(str(chat_id), text)
            except Exception as error:
                print("Агент не відповів:", error, file=sys.stderr)
                _send(token, chat_id, "Не вийшло відповісти. Причина в терміналі бота.")
                continue
            for start in range(0, len(answer), TELEGRAM_LIMIT):
                _send(token, chat_id, answer[start : start + TELEGRAM_LIMIT])


def _api(token, method, params=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None if params is None else json.dumps(params).encode()
    request = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.loads(response.read().decode())
    if not body.get("ok"):
        raise RuntimeError(body.get("description") or "Telegram error")
    return body["result"]


def _send(token, chat_id, text):
    _api(token, "sendMessage", {"chat_id": chat_id, "text": text})


if __name__ == "__main__":
    main()
