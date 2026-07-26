import json
import os

LOGGING_FILE = "data/logging.json"


def load_logging():
    if not os.path.exists(LOGGING_FILE):
        return {}

    with open(LOGGING_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_logging(data):
    with open(LOGGING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_guild_logging(guild_id: int):
    data = load_logging()
    return data.get(str(guild_id))


def update_guild_logging(guild_id: int, config: dict):
    data = load_logging()
    data[str(guild_id)] = config
    save_logging(data)


def remove_guild_logging(guild_id: int):
    data = load_logging()

    if str(guild_id) in data:
        del data[str(guild_id)]

    save_logging(data)