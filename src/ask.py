import sys

from src.chat import ask_agent


def main():
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print("Помилка: передай повідомлення. Наприклад: python -m src.ask Запам'ятай купити молоко", file=sys.stderr)
        raise SystemExit(1)
    print(ask_agent("terminal", text))


if __name__ == "__main__":
    main()
