import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tgapi import call


def main():
    p = argparse.ArgumentParser(description="Send rich HTML screens to a chat, each preceded by a label.")
    p.add_argument("--chat", required=True, type=int)
    p.add_argument("--title", help="Message sent before all screens")
    p.add_argument("--media", help="JSON file with InputRichMessageMedia list, shared by all screens")
    p.add_argument("--labels", choices=["footer", "message"], default="footer",
                   help="footer: label inside each screen (one message per screen); message: separate label messages")
    p.add_argument("items", nargs="+", help="Pairs: label file.html label file.html ...")
    a = p.parse_args()
    if len(a.items) % 2:
        raise SystemExit("items must be label/file pairs")
    media = json.loads(Path(a.media).read_text(encoding="utf-8")) if a.media else None
    if a.title:
        call("sendMessage", {"chat_id": a.chat, "text": a.title, "disable_notification": True})
    failed = 0
    for label, file in zip(a.items[::2], a.items[1::2]):
        html = Path(file).read_text(encoding="utf-8")
        if a.labels == "footer":
            safe = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html = f"{html}\n<footer>Preview · {safe}</footer>"
        rich = {"html": html}
        if media:
            used = [m for m in media if f"?id={m['id']}" in html]
            if used:
                rich["media"] = used
        if a.labels == "message":
            call("sendMessage", {"chat_id": a.chat, "text": label, "disable_notification": True})
        r = call("sendRichMessage", {"chat_id": a.chat, "rich_message": rich, "disable_notification": True})
        ok = r.get("ok")
        failed += not ok
        print(json.dumps({"label": label, "ok": ok, "message_id": (r.get("result") or {}).get("message_id"),
                          "error": r.get("description")}, ensure_ascii=False))
        time.sleep(0.4)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
