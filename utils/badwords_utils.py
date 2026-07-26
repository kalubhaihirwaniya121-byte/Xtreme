import json
import os

BADWORDS_FILE = "data/badwords.json"


def load_badwords():
    if not os.path.exists(BADWORDS_FILE):
        return {}

    with open(BADWORDS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_badwords(data):
    os.makedirs("data", exist_ok=True)

    with open(BADWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_badwords(guild_id: int):
    data = load_badwords()

    guild_id = str(guild_id)

    if guild_id not in data:
        data[guild_id] = []
        save_badwords(data)

    return data[guild_id]


def add_badword(guild_id: int, word: str):
    data = load_badwords()

    guild_id = str(guild_id)

    if guild_id not in data:
        data[guild_id] = []

    word = word.lower()

    if word not in data[guild_id]:
        data[guild_id].append(word)
        save_badwords(data)
        return True

    return False


def remove_badword(guild_id: int, word: str):
    data = load_badwords()

    guild_id = str(guild_id)

    if guild_id not in data:
        return False

    word = word.lower()

    if word in data[guild_id]:
        data[guild_id].remove(word)
        save_badwords(data)
        return True

    return False


def clear_badwords(guild_id: int):
    data = load_badwords()

    data[str(guild_id)] = []

    save_badwords(data)