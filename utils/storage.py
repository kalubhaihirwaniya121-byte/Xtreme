import json
import os

DATA_FOLDER = "data"

os.makedirs(DATA_FOLDER, exist_ok=True)


def load_json(filename):

    path = os.path.join(DATA_FOLDER, filename)

    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_json(filename, data):

    path = os.path.join(DATA_FOLDER, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4
        )