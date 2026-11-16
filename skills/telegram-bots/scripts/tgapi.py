import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8")

def token():
    if os.environ.get("BOT_TOKEN"):
        return os.environ["BOT_TOKEN"]
    env = Path.cwd() / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("BOT_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("BOT_TOKEN not found in the environment or ./.env")


def call(method, payload=None, timeout=60):
    url = f"https://api.telegram.org/bot{token()}/{method}"
    req = urllib.request.Request(url, json.dumps(payload or {}).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())
