import json
import os
from datetime import timedelta

AUTOMOD_FILE = "data/automod.json"


def load_automod():
    if not os.path.exists(AUTOMOD_FILE):
        return {}

    with open(AUTOMOD_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_automod(data):
    os.makedirs("data", exist_ok=True)

    with open(AUTOMOD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_guild_config(guild_id: int):
    data = load_automod()

    guild_id = str(guild_id)

    if guild_id not in data:
        data[guild_id] = {
            "enabled": False,
            "punishment": {
                "type": "warn",
                "duration": 600
            },
            "bypass_roles": [],
            "anti_links": False,
            "anti_invites": False,
            "anti_spam": False,
            "max_mentions": 5
        }

        save_automod(data)
    else:
        updated = False
        if "anti_links" not in data[guild_id]:
            data[guild_id]["anti_links"] = False
            updated = True
        if "anti_invites" not in data[guild_id]:
            data[guild_id]["anti_invites"] = False
            updated = True
        if "anti_spam" not in data[guild_id]:
            data[guild_id]["anti_spam"] = False
            updated = True
        if "max_mentions" not in data[guild_id]:
            data[guild_id]["max_mentions"] = 5
            updated = True
        if updated:
            save_automod(data)

    return data[guild_id]


def update_guild_config(guild_id: int, config: dict):
    data = load_automod()

    data[str(guild_id)] = config

    save_automod(data)


def parse_duration(duration: str):
    """
    Examples:
    30s
    10m
    2h
    1d
    """

    duration = duration.lower()

    if len(duration) < 2:
        return None

    unit = duration[-1]

    try:
        value = int(duration[:-1])
    except ValueError:
        return None

    if unit == "s":
        return timedelta(seconds=value)

    elif unit == "m":
        return timedelta(minutes=value)

    elif unit == "h":
        return timedelta(hours=value)

    elif unit == "d":
        return timedelta(days=value)

    return None


def duration_to_seconds(duration: str):
    td = parse_duration(duration)

    if td is None:
        return None

    return int(td.total_seconds())


def is_bypass(member, config):
    if member.guild_permissions.administrator:
        return True

    bypass_roles = config.get("bypass_roles", [])

    for role in member.roles:
        if role.id in bypass_roles:
            return True

    return False