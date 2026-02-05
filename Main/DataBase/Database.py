import json
from pathlib import Path

DATA_FILE = Path("data/data.json")
app.py
def load_data():
    """Read JSON file -> Python dict"""
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text('{"students": []}', encoding="utf-8")

    return json.loads(DATA_FILE.read_text(encoding="utf-8"))

def save_data(data):
    """Python dict -> write JSON file"""
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
