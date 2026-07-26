import json
import os

COUNTING_FILE = "data/counting.json"


def load_counting():
    if not os.path.exists(COUNTING_FILE):
        return {}

    with open(COUNTING_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_counting(data):
    os.makedirs("data", exist_ok=True)

    with open(COUNTING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_guild_data(guild_id: int):
    data = load_counting()

    guild_id = str(guild_id)

    if guild_id not in data:
        data[guild_id] = {
            "enabled": False,
            "channel": None,
            "current": 1,
            "current_streak": 0,
            "best_streak": 0,
            "last_user": 0,
            "user_stats": {}
        }

        save_counting(data)

    return data[guild_id]


def update_guild_data(guild_id: int, guild_data: dict):
    data = load_counting()

    data[str(guild_id)] = guild_data

    save_counting(data)


def get_user_stats(guild_data: dict, user_id: int):
    user_id = str(user_id)

    if user_id not in guild_data["user_stats"]:
        guild_data["user_stats"][user_id] = {
            "correct": 0,
            "broken": 0,
            "best_streak": 0
        }

    return guild_data["user_stats"][user_id]