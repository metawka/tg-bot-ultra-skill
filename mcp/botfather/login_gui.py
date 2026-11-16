import asyncio
import locale
import logging
import queue
import threading
import tkinter as tk
import traceback

import qrcode
from PIL import ImageTk
from telethon import TelegramClient
from datetime import datetime, timedelta, timezone

from telethon.errors import (ApiIdInvalidError, FloodWaitError, PasswordHashInvalidError, PhoneCodeExpiredError,
                             PhoneCodeInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError)

from common import CONFIG, HOME, SESSION, load_config, save_config

BG, FG, MUTED, ACCENT, ERROR = "#1c1c1e", "#f2f2f7", "#98989f", "#2f80ed", "#ff6b6b"
HOME.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=HOME / "login.log", level=logging.INFO, encoding="utf-8",
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("login")

TEXT = {
    "en": {
        "title": "Telegram sign-in", "keys": "App keys", "keys_hint": "my.telegram.org → API development tools",
        "save": "Save", "paste": "Paste", "bad_id": "API ID must contain digits only",
        "bad_hash": "API hash must be 32 characters (0-9, a-f)", "connecting": "Connecting",
        "qr": "Sign in with QR code", "qr_hint": "Telegram on the phone → Settings → Devices → Link Desktop Device",
        "qr_auto": "The code refreshes automatically", "password": "Cloud password",
        "bad_password": "Wrong password", "sign_in": "Sign in", "done": "Signed in", "account": "Account: {}",
        "error": "Sign-in error", "log": "Details: {}",
        "bad_keys": "Telegram rejected these keys. Copy API ID and API hash from my.telegram.org again",
        "use_phone": "Sign in with phone number", "use_qr": "Sign in with QR code", "phone": "Sign in with phone number",
        "phone_hint": "Number in international format, for example +44 7700 900000", "get_code": "Get code",
        "code": "Confirmation code", "code_hint": "The code arrives in Telegram on another device or by SMS",
        "bad_phone": "Telegram does not accept this number", "bad_code": "Wrong code",
        "code_expired": "The code has expired, request a new one", "flood": "Too many attempts, try again in {} s",
        "other_number": "Another number",
    },
    "ru": {
        "title": "Вход в Telegram", "keys": "Ключи приложения", "keys_hint": "my.telegram.org → API development tools",
        "save": "Сохранить", "paste": "Вставить", "bad_id": "API ID состоит только из цифр",
        "bad_hash": "API hash: 32 символа (0-9, a-f)", "connecting": "Подключение",
        "qr": "Вход по QR-коду", "qr_hint": "Telegram на телефоне → Настройки → Устройства → Подключить устройство",
        "qr_auto": "Код обновляется автоматически", "password": "Облачный пароль",
        "bad_password": "Неверный пароль", "sign_in": "Войти", "done": "Вход выполнен", "account": "Аккаунт: {}",
        "error": "Ошибка входа", "log": "Подробности: {}",
        "bad_keys": "Telegram не принял ключи. Скопировать API ID и API hash с my.telegram.org заново",
        "use_phone": "Вход по номеру телефона", "use_qr": "Вход по QR-коду", "phone": "Вход по номеру телефона",
        "phone_hint": "Номер в международном формате, например +7 900 000 00 00", "get_code": "Получить код",
        "code": "Код подтверждения", "code_hint": "Код приходит в Telegram на другом устройстве или по SMS",
        "bad_phone": "Telegram не принимает этот номер", "bad_code": "Неверный код",
        "code_expired": "Срок действия кода истёк, нужен новый", "flood": "Слишком много попыток, повтор через {} с",
        "other_number": "Другой номер",
    },
}


def lang():
    try:
        import ctypes
        code = locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), "")
    except Exception:
        code = locale.getlocale()[0] or ""
    return "ru" if code.lower().startswith(("ru", "russian")) else "en"


T = TEXT[lang()]


# Worker
class Worker(threading.Thread):
    def __init__(self, api_id, api_hash, events, inputs):
        super().__init__(daemon=True)
        self.api_id, self.api_hash = api_id, api_hash
        self.events, self.inputs = events, inputs

    def run(self):
        asyncio.run(self.main())

    async def get(self):
        return await asyncio.get_running_loop().run_in_executor(None, self.inputs.get)

    def peek(self):
        try:
            return self.inputs.get_nowait()
        except queue.Empty:
            return None

    async def main(self):
        client = TelegramClient(str(SESSION), self.api_id, self.api_hash)
        try:
            await client.connect()
            mode = None if await client.is_user_authorized() else "qr"
            while mode:
                mode = await (self.qr(client) if mode == "qr" else self.phone(client))
            me = await client.get_me()
            log.info("signed in as id %s", me.id)
            self.events.put(("done", me.first_name or me.username or str(me.id)))
        except ApiIdInvalidError:
            log.error("invalid api_id/api_hash")
            CONFIG.unlink(missing_ok=True)
            self.events.put(("bad_keys", None))
        except Exception as e:
            log.error("worker failed: %s", traceback.format_exc())
            self.events.put(("error", f"{type(e).__name__}: {e}"))
        finally:
            await client.disconnect()

    async def qr(self, client):
        login = await client.qr_login()
        self.events.put(("qr", login.url))
        while True:
            try:
                await login.wait(timeout=2)
                return None
            except asyncio.TimeoutError:
                if self.peek() == ("phone",):
                    return "phone"
                if datetime.now(timezone.utc) >= login.expires - timedelta(seconds=3):
                    await login.recreate()
                    self.events.put(("qr", login.url))
            except SessionPasswordNeededError:
                await self.password(client)
                return None

    async def phone(self, client):
        note = None
        while True:
            self.events.put(("phone", note))
            cmd = await self.get()
            if cmd == ("qr",):
                return "qr"
            if cmd[0] != "number":
                continue
            number = cmd[1]
            try:
                sent = await client.send_code_request(number)
            except PhoneNumberInvalidError:
                note = T["bad_phone"]
                continue
            except FloodWaitError as e:
                note = T["flood"].format(e.seconds)
                continue
            note = None
            while True:
                self.events.put(("code", note))
                cmd = await self.get()
                if cmd == ("back",):
                    note = None
                    break
                if cmd[0] != "code":
                    continue
                try:
                    await client.sign_in(phone=number, code=cmd[1], phone_code_hash=sent.phone_code_hash)
                    return None
                except PhoneCodeInvalidError:
                    note = T["bad_code"]
                except PhoneCodeExpiredError:
                    note = T["code_expired"]
                    break
                except SessionPasswordNeededError:
                    await self.password(client)
                    return None

    async def password(self, client):
        self.events.put(("password", None))
        while True:
            cmd = await self.get()
            if cmd[0] != "password":
                continue
            try:
                await client.sign_in(password=cmd[1])
                return
            except PasswordHashInvalidError:
                self.events.put(("bad_password", None))


# Window
class App:
    def __init__(self):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        self.root = tk.Tk()
        self.root.report_callback_exception = self.on_error
        self.k = self.root.winfo_fpixels("1i") / 96
        self.root.title(T["title"])
        self.root.configure(bg=BG)
        self.root.geometry(f"{self.px(380)}x{self.px(540)}")
        self.root.resizable(False, False)
        self.root.bind_all("<Control-KeyPress>", self.shortcut)
        self.events, self.inputs = queue.Queue(), queue.Queue()
        self.body = tk.Frame(self.root, bg=BG)
        self.body.pack(fill="both", expand=True, padx=self.px(24), pady=self.px(24))
        cfg = load_config()
        self.keys_form() if cfg is None else self.start(*cfg)

    def on_error(self, *args):
        log.error("ui failed: %s", "".join(traceback.format_exception(*args)))
        self.show_error(f"{args[0].__name__}: {args[1]}")

    def shortcut(self, e):
        actions = {86: "<<Paste>>", 67: "<<Copy>>", 88: "<<Cut>>"}
        w = self.root.focus_get()
        if e.keycode in actions and isinstance(w, tk.Entry) and e.keysym.lower() not in ("v", "c", "x"):
            w.event_generate(actions[e.keycode])
            return "break"
        if e.keycode == 65 and isinstance(w, tk.Entry):
            w.select_range(0, "end")
            w.icursor("end")
            return "break"

    def px(self, v):
        return int(v * self.k)

    def clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def label(self, text, color=FG, size=11, bold=False):
        lbl = tk.Label(self.body, text=text, bg=BG, fg=color, font=("Segoe UI", size, "bold" if bold else "normal"),
                       wraplength=self.px(330), justify="left")
        lbl.pack(anchor="w", pady=(0, 8))
        return lbl

    def entry(self, show=None):
        row = tk.Frame(self.body, bg=BG)
        row.pack(fill="x", pady=(0, 12))
        e = tk.Entry(row, bg="#2c2c2e", fg=FG, insertbackground=FG, relief="flat", font=("Segoe UI", 11), show=show)
        e.pack(side="left", fill="x", expand=True, ipady=6)

        def paste():
            try:
                e.delete(0, "end")
                e.insert(0, self.root.clipboard_get().strip())
            except tk.TclError:
                pass

        tk.Button(row, text=T["paste"], command=paste, bg="#3a3a3c", fg=FG, relief="flat", activebackground="#48484a",
                  font=("Segoe UI", 9)).pack(side="left", padx=(6, 0), ipady=4, ipadx=6)
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=T["paste"], command=paste)
        e.bind("<Button-3>", lambda ev: menu.tk_popup(ev.x_root, ev.y_root))
        return e

    def button(self, text, cmd):
        tk.Button(self.body, text=text, command=cmd, bg=ACCENT, fg="white", relief="flat", activebackground=ACCENT,
                  font=("Segoe UI", 11, "bold")).pack(fill="x", ipady=6, pady=(8, 0))

    def link(self, text, cmd):
        tk.Button(self.body, text=text, command=cmd, bg=BG, fg=ACCENT, relief="flat", bd=0, activebackground=BG,
                  activeforeground=ACCENT, cursor="hand2", font=("Segoe UI", 10)).pack(fill="x", pady=(10, 0))

    def submit(self, cmd):
        self.root.unbind("<Return>")
        self.inputs.put(cmd)

    def keys_form(self, message=""):
        self.clear()
        self.label(T["keys"], size=14, bold=True)
        self.label(T["keys_hint"], MUTED, 10)
        self.label("API ID", MUTED, 10)
        api_id = self.entry()
        api_id.focus_set()
        self.label("API hash", MUTED, 10)
        api_hash = self.entry()
        status = self.label(message, ERROR, 10)

        def save():
            i, h = api_id.get().strip(), api_hash.get().strip().lower()
            if h.isdigit() and not i.isdigit():
                i, h = h, i.lower()
                api_id.delete(0, "end")
                api_id.insert(0, i)
                api_hash.delete(0, "end")
                api_hash.insert(0, h)
            if not i.isdigit():
                status.config(text=T["bad_id"])
                return
            if len(h) != 32 or any(c not in "0123456789abcdef" for c in h):
                status.config(text=T["bad_hash"])
                return
            save_config(i, h)
            log.info("keys saved")
            self.start(*load_config())

        self.button(T["save"], save)
        self.root.bind("<Return>", lambda _: save())

    def start(self, api_id, api_hash):
        self.clear()
        self.root.unbind("<Return>")
        self.label(T["connecting"], MUTED)
        Worker(api_id, api_hash, self.events, self.inputs).start()
        self.root.after(200, self.poll)

    def show_qr(self, url):
        self.clear()
        self.label(T["qr"], size=14, bold=True)
        self.label(T["qr_hint"], MUTED, 10)
        img = qrcode.make(url, border=2).resize((self.px(260), self.px(260)))
        self.photo = ImageTk.PhotoImage(img)
        tk.Label(self.body, image=self.photo, bg=BG).pack(pady=8)
        self.label(T["qr_auto"], MUTED, 9)
        self.link(T["use_phone"], lambda: self.inputs.put(("phone",)))

    def form(self, title, hint, note, action, cmd, show=None, back=None):
        self.clear()
        self.label(title, size=14, bold=True)
        if hint:
            self.label(hint, MUTED, 10)
        if note:
            self.label(note, ERROR, 10)
        e = self.entry(show=show)
        e.focus_set()
        value = (lambda: e.get()) if show else (lambda: e.get().strip())
        go = lambda *_: value() and self.submit((cmd, value()))
        self.button(action, go)
        self.root.bind("<Return>", go)
        if back:
            self.link(*back)

    def show_phone(self, note=None):
        self.form(T["phone"], T["phone_hint"], note, T["get_code"], "number",
                  back=(T["use_qr"], lambda: self.submit(("qr",))))

    def show_code(self, note=None):
        self.form(T["code"], T["code_hint"], note, T["sign_in"], "code",
                  back=(T["other_number"], lambda: self.submit(("back",))))

    def show_password(self, error=False):
        self.form(T["password"], None, T["bad_password"] if error else None, T["sign_in"], "password", show="•")

    def show_error(self, text):
        self.clear()
        self.label(T["error"], size=14, bold=True)
        self.label(text, MUTED, 10)
        self.label(T["log"].format(HOME / "login.log"), MUTED, 9)

    def poll(self):
        while not self.events.empty():
            kind, data = self.events.get()
            if kind == "qr":
                self.show_qr(data)
            elif kind == "phone":
                self.show_phone(data)
            elif kind == "code":
                self.show_code(data)
            elif kind in ("password", "bad_password"):
                self.show_password(kind == "bad_password")
            elif kind == "done":
                self.clear()
                self.label(T["done"], size=14, bold=True)
                self.label(T["account"].format(data), MUTED)
                self.root.after(2500, self.root.destroy)
                return
            elif kind == "bad_keys":
                self.keys_form(T["bad_keys"])
                return
            elif kind == "error":
                self.show_error(data)
                return
        self.root.after(200, self.poll)


# Main
if __name__ == "__main__":
    try:
        App().root.mainloop()
    except Exception:
        log.error("fatal: %s", traceback.format_exc())
        raise
