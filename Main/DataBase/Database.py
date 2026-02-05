import json
from pathlib import Path

DATA_FILE = Path("data/data.json")

def load_data():
    """Read JSON file -> Python dict"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """Python dict -> write JSON file"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
