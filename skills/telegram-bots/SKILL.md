---
name: telegram-bots
description: Build Telegram bots that look current, using Bot API 10.x rich messages (tables, headings, in-message buttons, collapsible blocks, slideshows, maps, streamed drafts), colored buttons and custom emoji icons. Covers the whole path from a detailed interview with the owner, through creating the bot in @BotFather via the botfather MCP server, choosing between Telegram Serverless and a regular server, designing every screen, to setting up the bot profile. Use whenever the user wants to create, redesign, or extend a Telegram bot, asks for "a bot for my shop / salon / channel / community", mentions @BotFather, inline buttons, bot menus, Mini Apps, or wants a bot to look better.
---

# Telegram bots

This skill builds Telegram bots on current Bot API capabilities. Most bots, and most agents, still use 2020 patterns: a wall of text, a reply keyboard as the main menu, colorful emoji as icons, a new message for every screen. The goal here is the opposite: every screen is a structured rich message, actions are buttons inside the message, navigation edits one message in place.

## Workflow

Run the phases in order. Do not write bot code before phase 2 is confirmed.

| Phase | What happens | Reference |
|---|---|---|
| 0. Bot | Create the bot or connect an existing one, learn the owner's chat id and Premium status | `references/bot-setup.md` |
| 1. Interview | Detailed interview about product and style, with live previews sent to the bot chat | `references/interview.md` |
| 2. Summary | One table of all decisions, owner confirms | `references/interview.md` |
| 3. Hosting | Claude picks Serverless or a regular server and states why in one line | `references/hosting.md` |
| 4. Screens | Build every screen from rich message patterns | `references/design-rules.md`, `references/rich-messages.md`, `references/icons.md` |
| 5. Profile | Name, descriptions, commands, menu button, photo | `references/bot-setup.md` |
| 6. Check | Send every screen to the owner chat, collect feedback, fix | `references/verification.md` |

For changes to an existing bot, skip phase 0 when a token exists, run the interview only for the screens being changed, and keep the bot's established style.

## Hard rules

1. **Rich messages first.** Every screen is sent with `sendRichMessage` (or edited with `editMessageText` + `rich_message`) using the `html` field. Plain `sendMessage` with `parse_mode` is a fallback only for chats or clients where rich messages are not allowed, and the reason is stated.
2. **Buttons live inside the message.** Use `<tg-button-row>` blocks inside the rich message. A reply keyboard is never the main menu.
3. **One screen, one message.** Navigation edits the current message. New messages are for events the user should keep in history: confirmations, receipts, notifications.
4. **Color means something.** `success` finishes or confirms, `danger` cancels or deletes, `primary` marks the single main action. Everything else stays neutral.
5. **Icons from one adaptive pack.** Custom emoji icons only from one pack per bot, preferably an adaptive one that takes the text color. Never mix packs, never mix custom icons with regular colorful emoji. See `references/icons.md`.
6. **No Premium, no custom emoji.** Custom emoji in bot messages and button icons work only if the bot owner has Telegram Premium. Without it, use the no-Premium layout from `references/design-rules.md`.
7. **No fake images.** Never generate placeholder banners, gradient cards with the bot name, or schematic product pictures. Images appear only when they are real (owner photos, product photos) or generated in a style the owner approved in the interview.
8. **Texts are for the bot's users.** Descriptions and greetings describe the business, not the bot's features. Use only facts the owner gave; never invent addresses, hours, prices, or experience.
9. **The owner decides taste, Claude decides technology.** Ask about behavior and look. Never ask about language, framework, hosting, database, or webhook versus polling.
10. **/start heads the command menu.** `/start` is always the first command in `setMyCommands`, with a description like "Main menu". Staff and admin commands never appear in the public list: set them per chat with `BotCommandScopeChat`.
11. **Check the API before trusting memory.** Rich messages appeared in Bot API 10.1 (June 2026) and change often. Before building, fetch `https://core.telegram.org/bots/api-changelog` (WebFetch, or `curl -s https://core.telegram.org/bots/api-changelog.md`; some scraping services are refused); if the newest version is above the one in `references/rich-messages.md`, read what changed.
12. **Sample data only in previews.** Interview previews may use invented items and prices, and the title message says they are samples. The built bot uses only the owner's data; when it is missing, the screen shows an empty state, not invented content.

## Tools in this skill

- `scripts/preview.py`: send one or more rich HTML screens to a chat, each labeled ("A", "B", "Start") in its footer. Used for interview previews and phase 6.
- `scripts/owner.py`: wait for /start in the bot and print the chat id, language, and `is_premium` of whoever sent it.
- `scripts/username.py`: check whether bot usernames are free.
- `scripts/pack.py`: dump a custom emoji pack (ids, base emoji) to JSON, for adding new icon packs.
- `assets/icon-roles.json`: icon ids by meaning (home, back, settings, user, ...) for the supported packs.

All scripts use only the Python standard library and read the bot token from the `BOT_TOKEN` environment variable or a `.env` file in the current directory.

## The botfather MCP server

Creating bots and changing settings that the Bot API does not expose goes through the `botfather` MCP server shipped with this repository. It can talk only to @BotFather. If its tools are missing, tell the owner how to install it (see the repository README) and fall back to the manual steps in `references/bot-setup.md`.
