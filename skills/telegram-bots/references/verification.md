# Verification

Claude cannot see how Telegram renders a message. The API only says whether it was accepted. Every screen therefore goes to the owner's chat before it is called done.

## Steps

1. Save each screen's HTML into a file, one per screen, named after the screen.
2. Send them with `python scripts/preview.py --chat <owner_chat_id> --title "Screens for review" Start start.html Catalog catalog.html` (label and file in pairs). The label goes into each screen's footer, one message per screen; `--labels message` sends labels as separate messages instead. Every send must return `"ok": true`; on an error, fix the HTML (unclosed tags, unsupported tags, button attributes) and resend.
3. Ask the owner, through AskUserQuestion, which screens look wrong, with "All fine" as the first option. Ask for a screenshot of any screen that rendered badly.
4. Fix and resend only the screens that changed.
5. Run the bot and walk the main scenarios with the owner: every button must answer (`answerCallbackQuery` on every callback, even when the screen just changes).

## Checklist before handing over

- Every callback is answered.
- Navigation edits one message; Back and Home work from every screen.
- No raw URLs in text, no reply keyboard as a menu.
- One icon pack everywhere, or no custom emoji at all without Premium.
- Button labels fit (about 14 characters per button in a two-button row).
- User data in HTML is escaped.
- Profile is set: name, description, short description, commands with `/start` first, menu button.
- Staff commands are set only for staff chats; a regular user does not see them in the menu.
- Numbers follow the format rule (no "+0", no "-0").
- The token is in `.env`, `.env` is in `.gitignore`.
