import json
import os


TRUTHS = []
DARES = []


def load_truth_dare():

    global TRUTHS
    global DARES

    truth_file = "data/truth.json"
    dare_file = "data/dare.json"

    if not os.path.exists(truth_file):
        with open(truth_file, "w") as f:
            json.dump([], f, indent=4)

    if not os.path.exists(dare_file):
        with open(dare_file, "w") as f:
            json.dump([], f, indent=4)

    with open(truth_file, "r", encoding="utf-8") as f:
        TRUTHS = json.load(f)

    with open(dare_file, "r", encoding="utf-8") as f:
        DARES = json.load(f)

    print(
        f"[TruthDare] Loaded {len(TRUTHS)} Truths & {len(DARES)} Dares."
    )