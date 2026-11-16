# Hosting

Claude chooses; the owner is told the choice and the reason in one line.

## Telegram Serverless

Telegram runs the bot's JavaScript in V8 isolates next to the Bot API, with a built-in SQLite database and optional Mini App hosting at `https://app<id>.tgcloud.ai/`. Docs: https://core.telegram.org/bots/serverless.

Choose it when the bot is menus, forms, requests, bookings, orders, notifications, user data in a few tables, calls to external APIs over `fetch`, and a Mini App with a light backend.

Limits that rule it out:
- npm packages are not available, only the SDK (`sdk`, `sdk/db`, `sdk/api`, `sdk/fetch`) and the project's own modules
- no file system, no Node `Buffer`, no sockets, no long-running or background processes
- uploads up to 50 MB (photos 10 MB), downloads up to 20 MB, `fetch` responses up to 30 MB
- SQLite only, foreign keys are disabled
- pricing and call limits are not published; check the page before promising anything about cost

Basics:
- Enable Serverless for the bot in the BotFather Mini App; get the CLI access token there (Serverless → CLI Access). The owner does this step.
- Scaffold `npm create @tgcloud/bot <name>`, link `npx tgcloud login`, deploy `npx tgcloud push`, apply schema changes `npx tgcloud migrate`, test a handler locally `npx tgcloud run handlers/message '{...}'`.
- Layout: `tgcloud/handlers/<update_type>.js`, `tgcloud/endpoints/<name>.js` (Mini App API, init data verified by the platform), `tgcloud/lib/`, `tgcloud/schema.js`.
- `api.<method>(params)` covers every Bot API method, including `sendRichMessage`.
- No scheduler: as of Bot API 10.4 the Serverless docs describe no cron or timed jobs. A bot that must send anything on its own at a set time (reminders, "your order is ready in 10 minutes", daily reports) needs a regular server. Re-check the docs; if scheduling appears, update this rule.

## Regular server

Choose it when any of the limits above applies, for payments with webhooks from external providers, media processing, AI with long jobs, external databases, or when the owner already has hosting.

Defaults:
- Python 3.11+, no bot framework: a small Bot API client over `httpx` calling methods by name. Frameworks lag behind new methods such as `sendRichMessage`; a thin client never does.
- Long polling for development, webhook behind HTTPS in production.
- SQLite for small bots, PostgreSQL when there are several workers or heavy writes.
- A scheduler (APScheduler or a simple loop) for reminders.
- Deploy on the owner's server with systemd, or on any container host.

## Decision

1. Any hard limit of Serverless applies, including timed messages → regular server.
2. Owner already pays for hosting and wants everything there → regular server.
3. Otherwise → Serverless.
4. When unsure, choose the regular server: moving from Serverless later means a rewrite.
