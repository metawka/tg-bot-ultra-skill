import json
import re
import sys
import urllib.request

VALID = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,30}(bot|_bot|Bot)$")


def taken(name):
    req = urllib.request.Request(f"https://t.me/{name}", headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return "tgme_page_title" in r.read().decode("utf-8", "ignore")


def main():
    out = []
    for name in sys.argv[1:]:
        name = name.lstrip("@")
        if not VALID.match(name):
            out.append({"username": name, "status": "invalid"})
            continue
        out.append({"username": name, "status": "taken" if taken(name) else "free"})
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
