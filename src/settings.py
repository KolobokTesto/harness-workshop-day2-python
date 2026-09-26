import os


def is_owner(chat_id):
    owner = os.environ.get("OWNER_CHAT_ID")
    return bool(owner) and chat_id == owner
