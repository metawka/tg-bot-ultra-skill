import argparse
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_SRC = ROOT / "skills" / "telegram-bots"
SKILL_DST = Path.home() / ".claude" / "skills" / "telegram-bots"
MCP = ROOT / "mcp" / "botfather"
VENV = MCP / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def step(text):
    print(f"\n› {text}")


def run(cmd, dry, check=True):
    print("  " + " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
    if not dry:
        return subprocess.run([str(c) for c in cmd], check=check)


def skill(dry):
    step("Skill")
    if SKILL_DST.exists() and SKILL_DST.resolve() == SKILL_SRC.resolve():
        print(f"  {SKILL_DST} already points to this repository")
        return
    print(f"  {SKILL_SRC} -> {SKILL_DST}")
    if dry:
        return
    if SKILL_DST.is_symlink() or (SKILL_DST.exists() and not SKILL_DST.is_dir()):
        SKILL_DST.unlink()
    elif SKILL_DST.exists():
        shutil.rmtree(SKILL_DST)
    SKILL_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL_SRC, SKILL_DST, ignore=shutil.ignore_patterns("__pycache__"))


def server(dry):
    step("MCP server environment")
    try:
        import tkinter
    except ImportError:
        sys.exit("  tkinter is missing in this Python. Install Python from python.org or add the tk package.")
    if not PY.exists():
        print(f"  creating {VENV}")
        if not dry:
            venv.create(VENV, with_pip=True)
    run([PY, "-m", "pip", "install", "-q", "-r", MCP / "requirements.txt"], dry)


def register(dry):
    step("Claude Code registration")
    claude = shutil.which("claude")
    cmd = ["claude", "mcp", "add", "--scope", "user", "botfather", "--", PY, MCP / "server.py"]
    if claude is None:
        print("  claude CLI not found. Run this after installing Claude Code:")
        print("  " + " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd))
        return
    if not dry and subprocess.run([claude, "mcp", "get", "botfather"], capture_output=True).returncode == 0:
        print("  botfather is already registered")
        return
    cmd[0] = claude
    run(cmd, dry)


def main():
    p = argparse.ArgumentParser(description="Install the telegram-bots skill and the botfather MCP server.")
    p.add_argument("--dry-run", action="store_true", help="Print the steps without changing anything")
    p.add_argument("--skill-only", action="store_true", help="Install only the skill")
    a = p.parse_args()
    if sys.version_info < (3, 11):
        sys.exit("Python 3.11 or newer is required")
    skill(a.dry_run)
    if not a.skill_only:
        server(a.dry_run)
        register(a.dry_run)
    print("\nDone. Restart Claude Code to load the skill and the MCP server.")


if __name__ == "__main__":
    main()
