# Bot setup

## Creating a bot

### With the botfather MCP server (preferred)

The server talks to @BotFather from the owner's account and to nothing else.

1. `status`. If it reports missing keys or no sign-in, call `login`: a small window opens on the owner's computer, in the system language. The owner:
   - creates an app at my.telegram.org → API development tools (any title and short name, platform Desktop) and copies API ID and API hash into the window; the "Paste" buttons next to the fields work in any keyboard layout;
   - scans the QR code in Telegram on the phone: Settings → Devices → Link Desktop Device (in the Russian interface: Настройки → Устройства → Подключить устройство), or chooses "Sign in with phone number" in the window and enters the number and the code Telegram sends;
   - types the cloud password in the window, if the account has one.
   Claude never sees these values and must not ask for them in chat. After the owner says the window is done, call `status` again; it also returns the last error from the sign-in window.
2. **If sign-in fails once, do not loop.** Show the error from `status`, offer one retry, and in the same message offer the manual path below so the owner is not blocked. Continue the interview with text mockups while the owner decides.
3. `create_bot(name, username, env_path)`. The token is written to `env_path` (absolute path to the project's `.env`) as `BOT_TOKEN`. If BotFather refuses (username taken or invalid), the reply text is returned: pick the next free username (`scripts/username.py`) and retry.
4. Ask the owner to open `https://t.me/<username>` and press Start, and run `python scripts/owner.py` in the project folder right away: it waits up to 90 seconds for the /start and prints the owner's chat id and `is_premium`. If it exits empty, ask the owner to send /start again and rerun it.

Sign-in timing: the owner may need a minute or two for my.telegram.org and the QR scan. After `login`, ask them to say when the window shows "Signed in" ("Вход выполнен"); if `status` still reports no sign-in, wait for the next answer instead of opening the window again.

Other tools: `get_token` for existing bots, `send` and `click` to walk BotFather menus (`/mybots` → bot → Bot Settings → Inline Mode, Domain, Menu Button, Group Privacy...), `screen` to read the current menu. Deleting bots, revoking tokens and transferring ownership are blocked; the owner does them by hand.

### Without the MCP server

Give the owner these steps, then ask them to put the token into the project's `.env` file themselves (not into the chat):
1. Open @BotFather, send `/newbot`.
2. Send the bot name, then the username ending in `bot`.
3. Copy the token from the reply into `.env` as `BOT_TOKEN=...`.

### Existing bot

If the project already has `BOT_TOKEN`, call `getMe` to confirm it works. If the owner has the bot but not the token, use `get_token`.

## Profile through the Bot API

All of these work with the token; BotFather is not needed.

| What | Method |
|---|---|
| Name | `setMyName` (`name`, optional `language_code`) |
| Description before Start, up to 512 chars | `setMyDescription` |
| Short description in the profile, up to 120 chars | `setMyShortDescription` |
| Commands with descriptions | `setMyCommands` (scopes and languages supported) |
| Menu button | `setChatMenuButton` (`commands` or `web_app`) |
| Profile photo | `setMyProfilePhoto` (InputProfilePhoto), `removeMyProfilePhoto` |
| Default admin rights | `setMyDefaultAdministratorRights` |

Set descriptions and commands for every interface language from interview question 1.8.

## Settings only in BotFather

Use the MCP `send`/`click` tools or give the owner the steps:
- Inline mode and its placeholder: Bot Settings → Inline Mode
- Group privacy, joining groups: Bot Settings → Group Privacy, Allow Groups
- Domain for Login Widget and Mini Apps: Bot Settings → Domain
- Mini App setup: Bot Settings → Configure Mini App, `/newapp`
- Payments providers: Bot Settings → Payments
- Description picture: Edit Bot → Edit Description Picture

Settings that live only in the BotFather Mini App (open @BotFather, tap the app button), for example Serverless and managed bots, cannot be reached by the MCP server. Give the owner one short instruction and wait for "done".

## Security

- The token goes to `.env` only. Add `.env` to `.gitignore`. Never print it in chat or commit it.
- If a token was exposed, the owner revokes it in BotFather (API Token → Revoke) and the new one goes through `get_token`.
