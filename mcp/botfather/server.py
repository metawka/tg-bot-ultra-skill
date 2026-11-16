import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from telethon import TelegramClient

from common import HOME, SESSION, load_config

ROOT = Path(__file__).resolve().parent
BOTFATHER = "BotFather"
TOKEN_RE = re.compile(r"\b\d{6,12}:[A-Za-z0-9_-]{30,}\b")
BLOCKED_CMD = re.compile(r"^/(deletebot|revoke|deleteapp|deletegame)\b", re.I)
BLOCKED_BTN = re.compile(r"delete|revoke|transfer|sure|удал|перевыпус|переда", re.I)

mcp = MCPServer(
    "botfather",
    instructions=(
        "Access to the @BotFather chat of the signed-in Telegram account and nothing else. "
        "Bot tokens are never returned in full: create_bot and get_token write them to an .env file. "
        "Deleting bots, revoking tokens and transferring ownership are not available here; the user does them manually."
    ),
)
state = {"client": None}
lock = asyncio.Lock()


# Client
async def client():
    c = state["client"]
    if c is None:
        cfg = load_config()
        if cfg is None:
            raise RuntimeError("Нет ключей приложения. Вызвать login и заполнить API ID и API hash в окне входа.")
        c = TelegramClient(str(SESSION), *cfg)
        state["client"] = c
    if not c.is_connected():
        await c.connect()
    if not await c.is_user_authorized():
        raise RuntimeError("Вход не выполнен. Вызвать login и отсканировать QR-код в окне входа.")
    return c


async def release():
    c = state["client"]
    if c is not None and c.is_connected():
        await c.disconnect()
    state["client"] = None


def mask(text):
    return TOKEN_RE.sub("<токен скрыт>", text or "")


def render(msgs):
    out = []
    for m in msgs:
        out.append(mask(m.raw_text))
        if m.buttons:
            out.append("Кнопки: " + " | ".join(" · ".join(b.text for b in row) for row in m.buttons))
    return "\n".join(out) if out else "BotFather не ответил"


async def replies(c, after_id, timeout=20):
    loop = asyncio.get_running_loop()
    end = loop.time() + timeout
    found = []
    while loop.time() < end:
        found = [m for m in await c.get_messages(BOTFATHER, min_id=after_id, limit=10) if not m.out]
        if found:
            await asyncio.sleep(1.0)
            found = [m for m in await c.get_messages(BOTFATHER, min_id=after_id, limit=10) if not m.out]
            return list(reversed(found))
        await asyncio.sleep(0.7)
    return found


async def say(c, text):
    sent = await c.send_message(BOTFATHER, text)
    msgs = await replies(c, sent.id)
    await asyncio.sleep(1.2)
    return msgs


def write_env(path, token, key):
    p = Path(path)
    if not p.is_absolute():
        raise ValueError("env_path должен быть абсолютным путём")
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    lines = [line for line in lines if not line.startswith(f"{key}=")] + [f"{key}={token}"]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def token_in(msgs):
    for m in msgs:
        t = TOKEN_RE.search(m.raw_text or "")
        if t:
            return t.group(0)
    return None


# Tools
def last_error():
    log = HOME / "login.log"
    if not log.exists():
        return ""
    errors = [line for line in log.read_text(encoding="utf-8", errors="ignore").splitlines() if " ERROR " in line]
    return f"\nПоследняя ошибка окна входа: {errors[-1][:300]}" if errors else ""


@mcp.tool(description="Signed-in account and readiness. Call first. Includes the last sign-in window error, if any.")
async def status() -> str:
    if load_config() is None:
        return "Нет ключей приложения. Нужен login." + last_error()
    try:
        c = await client()
    except RuntimeError as e:
        return str(e) + last_error()
    me = await c.get_me()
    return f"Готово. Аккаунт: {me.first_name or ''} @{me.username or '-'} (id {me.id})"


@mcp.tool(description="Open the local sign-in window (QR code, cloud password). The user completes it; then call status.")
async def login() -> str:
    await release()
    py = ROOT / ".venv" / "Scripts" / ("pythonw.exe" if os.name == "nt" else "python")
    if not py.exists():
        py = Path(sys.executable)
    subprocess.Popen([str(py), str(ROOT / "login_gui.py")], cwd=str(ROOT))
    return "Окно входа открыто на компьютере пользователя. После входа вызвать status."


@mcp.tool(description="Create a bot. Writes the token to env_path (absolute path to .env) under env_key. Returns username or BotFather's refusal text (e.g. username taken).")
async def create_bot(name: str, username: str, env_path: str, env_key: str = "BOT_TOKEN") -> str:
    async with lock:
        c = await client()
        await say(c, "/cancel")
        await say(c, "/newbot")
        await say(c, name)
        msgs = await say(c, username)
        token = token_in(msgs)
        if token is None:
            await say(c, "/cancel")
            return "Бот не создан. Ответ BotFather:\n" + render(msgs)
        write_env(env_path, token, env_key)
        return f"Создан @{username.lstrip('@')}. Токен записан в {env_path} ({env_key})."


@mcp.tool(description="Fetch the current token of an existing bot of this account and write it to env_path.")
async def get_token(username: str, env_path: str, env_key: str = "BOT_TOKEN") -> str:
    async with lock:
        c = await client()
        await say(c, "/cancel")
        await say(c, "/token")
        msgs = await say(c, "@" + username.lstrip("@"))
        token = token_in(msgs)
        if token is None:
            await say(c, "/cancel")
            return "Токен не получен. Ответ BotFather:\n" + render(msgs)
        write_env(env_path, token, env_key)
        return f"Токен @{username.lstrip('@')} записан в {env_path} ({env_key})."


@mcp.tool(description="Send a text or command to BotFather and return its reply with button labels. Destructive commands are refused.")
async def send(text: str) -> str:
    if BLOCKED_CMD.match(text.strip()):
        return "Команда недоступна через MCP, пользователь выполняет её вручную."
    async with lock:
        c = await client()
        return render(await say(c, text))


@mcp.tool(description="Press a button in BotFather's latest message by its label and return the updated screen. Destructive buttons are refused.")
async def click(label: str) -> str:
    if BLOCKED_BTN.search(label):
        return "Кнопка недоступна через MCP, пользователь нажимает её вручную."
    async with lock:
        c = await client()
        for m in await c.get_messages(BOTFATHER, limit=5):
            if m.out or not m.buttons:
                continue
            target = next((b for row in m.buttons for b in row if b.text.strip().lower() == label.strip().lower()), None)
            target = target or next((b for row in m.buttons for b in row if label.strip().lower() in b.text.lower()), None)
            if target is None:
                continue
            before = (m.raw_text, [[b.text for b in r] for r in m.buttons])
            await target.click()
            loop = asyncio.get_running_loop()
            end = loop.time() + 15
            while loop.time() < end:
                await asyncio.sleep(0.8)
                newer = [x for x in await c.get_messages(BOTFATHER, min_id=m.id, limit=10) if not x.out]
                if newer:
                    await asyncio.sleep(1.0)
                    return render(list(reversed([x for x in await c.get_messages(BOTFATHER, min_id=m.id, limit=10) if not x.out])))
                cur = await c.get_messages(BOTFATHER, ids=m.id)
                if cur and (cur.raw_text, [[b.text for b in r] for r in (cur.buttons or [])]) != before:
                    return render([cur])
            return "Экран не изменился"
        return f"Кнопка «{label}» не найдена в последних сообщениях BotFather"


@mcp.tool(description="Return BotFather's latest message with button labels.")
async def screen() -> str:
    async with lock:
        c = await client()
        for m in await c.get_messages(BOTFATHER, limit=5):
            if not m.out:
                return render([m])
        return "Сообщений от BotFather нет"


# Main
if __name__ == "__main__":
    mcp.run()
