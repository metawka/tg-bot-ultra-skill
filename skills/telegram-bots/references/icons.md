# Icons

Icons are custom emoji from public packs. They need the bot owner's Premium (see `rich-messages.md`).

## Supported packs

| Key | Pack | Icons | Color | Notes |
|---|---|---|---|---|
| `ios` | `tgiosicons` | 399 | adaptive | Telegram's own iOS line icons. Default. No scissors, no cart |
| `sf` | `SFSymbols` | 887 | adaptive | Apple SF Symbols. Widest coverage: scissors, calendar, devices, sports, food |
| `phosphor` | `PhosphorIcons` | 165 | adaptive | Thin modern lines, has a ruble sign, charts, trophy |
| `material` | `material_icons` | 87 | adaptive | Android outline. No check, no calendar; offer last |
| `md3` | `MD3Icons` | 56 | fixed peach | Material Expressive badges. Only for brands with a matching color |
| `tgfill` | `interface_icons` | 200 | fixed blue | Telegram Android filled icons. Only for blue brands |
| `ui_anim` | `ui_icons` | 137 | adaptive, animated | Moving icons; use sparingly, on start screens and main actions |

Adaptive icons take the text color, so they work in light and dark themes and with any accent. Prefer them.

Add a pack to a message with `<tg-emoji emoji-id="ID">alt</tg-emoji>`; the alt is the pack's base emoji for that icon (stored in `assets/icon-roles.json`). Users can add a pack with `https://t.me/addemoji/<pack>`.

## Roles

`assets/icon-roles.json` maps meanings to icons:

```json
{"packs": {"ios": {"name": "tgiosicons", "roles": {"home": {"id": "...", "alt": "🏠"}}}}}
```

Roles available for most packs: home, back, settings, user, users, chat, search, bell, check, cross, info, help, warn, star, heart, gift, coin, wallet, tag, percent, pin, clock, calendar, chart, box, store, plus, edit, trash, refresh, copy, phone, lock, link, filter, bolt, sparkles, crown, book.

Coverage differs by pack. Before recommending a pack, list the roles the bot needs and check each pack. If a role is missing in the chosen pack, look for it with `scripts/pack.py` (it dumps every icon with its base emoji; open the pack link to see the shapes), or choose a pack that has it. Never fill a gap with an icon from another pack.

## Adding a pack

1. Find a pack link `t.me/addemoji/<name>`.
2. `python scripts/pack.py <name> > pack.json` (needs any bot token).
3. Check `sticker_type` is `custom_emoji` and `needs_repainting` is true for adaptive packs.
4. Add the roles you identified to `assets/icon-roles.json`.

## Without Premium

No custom emoji at all. Do not substitute regular colorful emoji. Follow "Without Premium" in `design-rules.md`.
