import json
import os
from pathlib import Path

HOME = Path(os.environ.get("TG_BOTFATHER_HOME", Path.home() / ".tg-botfather"))
CONFIG = HOME / "config.json"
SESSION = HOME / "botfather"


def load_config():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return int(data["api_id"]), data["api_hash"]
    except (FileNotFoundError, KeyError, ValueError):
        return None


def save_config(api_id, api_hash):
    HOME.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(json.dumps({"api_id": int(api_id), "api_hash": api_hash.strip()}), encoding="utf-8")
