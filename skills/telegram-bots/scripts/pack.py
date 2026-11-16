import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tgapi import call


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: pack.py <pack_short_name>")
    r = call("getStickerSet", {"name": sys.argv[1]})
    if not r.get("ok"):
        raise SystemExit(r.get("description"))
    s = r["result"]
    items = s["stickers"]
    print(json.dumps({
        "name": s["name"],
        "title": s["title"],
        "type": s["sticker_type"],
        "adaptive": all(x.get("needs_repainting") for x in items),
        "link": f"https://t.me/addemoji/{s['name']}",
        "icons": [{"index": i, "id": x.get("custom_emoji_id"), "alt": x.get("emoji")} for i, x in enumerate(items)],
    }, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
