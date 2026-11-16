import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tgapi import call


def collect(updates, seen):
    for u in updates:
        m = u.get("message") or {}
        f = m.get("from") or {}
        if m.get("chat", {}).get("type") == "private" and f:
            seen[f["id"]] = {"chat_id": m["chat"]["id"], "name": f.get("first_name"), "username": f.get("username"),
                             "language": f.get("language_code"), "is_premium": bool(f.get("is_premium")),
                             "text": m.get("text")}


def main():
    p = argparse.ArgumentParser(description="Wait for /start in the bot and print who sent it.")
    p.add_argument("--wait", type=int, default=90, help="Seconds to wait for a private message")
    a = p.parse_args()
    me = call("getMe")
    if not me.get("ok"):
        raise SystemExit(me.get("description"))
    seen = {}
    end = time.time() + a.wait
    while True:
        left = max(0, int(end - time.time()))
        r = call("getUpdates", {"timeout": min(25, left), "allowed_updates": ["message"]}, timeout=40)
        collect(r.get("result", []), seen)
        if seen or left == 0:
            break
    print(json.dumps({"bot": "@" + me["result"]["username"], "users": list(seen.values())}, ensure_ascii=False, indent=1))
    if not seen:
        print("No /start yet: ask the owner to open the bot, press Start (or send /start again), then run again.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
