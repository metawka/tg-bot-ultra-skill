# Interview

The interview runs before any code. Its job is to collect every product and style decision that Claude must not make alone. Technical decisions (stack, hosting, storage, libraries) are Claude's; they are reported in one line in the summary.

## How to run it

1. **Batches.** Ask through AskUserQuestion, up to 4 questions per call, several calls per round. Never ask one question at a time in plain text.
2. **Recommendation first.** The first option of every question is Claude's recommendation, marked "(recommended)". It follows `design-rules.md` and earlier answers.
3. **Skip what can be derived.** If the answer follows from the request, the project, earlier answers, or the rules, do not ask; put the conclusion into the summary.
4. **A tree, not a form.** Each answer opens or closes branches. Ask a question only when its condition holds.
5. **Previews for every visual fork.** When options differ in how they look, the owner sees them first:
   - the bot exists and the owner chat id is known: send the options to the bot chat with `scripts/preview.py`, labeled "A", "B", "C", and refer to the labels in the question; previews may use sample items and prices, and the `--title` says so;
   - no bot yet: put a text mockup into the `preview` field of the option.
   Describing a look in words without a preview is not allowed.
6. **Detailed on taste.** If two or more options are equally good under the rules, the owner decides. Do not pick silently, even when confident. Such questions have no "(recommended)" mark.
7. **Combined options.** For layout questions, add a combined option when two layouts can work in sequence (for example, "table to pick a master, then a slot grid").
8. **Language.** Ask in the language the owner writes in. Bot interface language is a separate question (1.8).
9. **Existing bots.** For changes, interview only about the affected screens.
10. **Summary.** After the last round, show one table with every decision, including derived ones, and wait for confirmation.

## Rounds

| Round | Topic | When |
|---|---|---|
| 0 | Bot | No bot yet. Runs first so style questions can use live previews |
| 1 | Product | Always |
| 2 | Objects and data | Always |
| 3 | General style | Always |
| 4 | Screen layouts | For each screen type the bot has |
| 5 | Bot profile | Always |
| 6 | Summary | Always |

## Round 0. Bot

A username is permanent: the Bot API cannot change it, and a new one means a new bot. So round 0 asks only what the username needs:
- the business or project name, if the request does not have it;
- 5.1 name and 5.2 username, with 3 free usernames checked by `scripts/username.py`.
The display name can still change later with `setMyName`.

Then follow `bot-setup.md`: create the bot through the botfather MCP server, ask the owner to open the bot and press Start, and run `scripts/owner.py`, which waits for that /start. It gives the chat id and `is_premium`; `is_premium` answers 3.6.

If the owner declines to create a bot now, use text mockups for previews.

## Round 1. Product

**1.1 Purpose.** What the bot does, in one sentence. Offer 2-3 wordings of different scope built from the request. Skip if the request is unambiguous.

**1.2 Users.**
- Customers of a business
- Members of a community or channel
- A team, internal tool
- Only the owner

**1.3 Roles.** Condition: 1.2 is not "Only the owner".
- User and admin (recommended for customer bots)
- Only user
- User, staff (master, courier, moderator), admin

**1.4 Main scenarios.** multiSelect, options built from the purpose. At most 6 at launch; the rest goes to "later".

**1.5 Where the bot works.** multiSelect.
- Private chats (recommended)
- Groups
- Channels
- Inline mode in any chat

**1.5a Inline mode.** Condition: inline mode selected. What can be shared through @bot in another chat: price list, an object card, an invitation.

**1.6 Money.**
- No payments
- Telegram Stars
- Card payment through a provider or link
- Subscription

**1.6a Prepayment.** Condition: payment for a service or booking.
- Fixed amount
- Percentage
- Full payment

**1.6b Refunds on cancellation.** Condition: any payment.
- Refund if cancelled earlier than N hours (recommended, ask N)
- No refunds
- Reschedule instead of refund

**1.7 Mini App.**
- Not needed, everything in messages (recommended when each action fits in 1-3 screens)
- For some scenarios
- Main interface
Recommend a Mini App when 1.4 has long forms, builders, big filtered catalogs, or charts.

**1.8 Interface language.**
- One language (the owner's)
- Two languages by the user's Telegram language
- Other set

**1.9 Business facts.** Needed for descriptions and "About" screens. Ask for free text (the "Other" field) unless the request already has them: address, hours, what makes the business different, prices "from", contacts. Never invent facts; a missing fact is left out of every text.
If the owner answers "later": build without an "About" screen and without facts in descriptions (the description then says only what the business is, from the name and purpose), and add "business facts, About screen" to the handover list.

## Round 2. Objects and data

**2.1 Main object.** What screens are built around: product, booking, request, order, task, post. Usually derived from the purpose.

**2.2 Object fields.** multiSelect per object: what the object card shows. Claude proposes, the owner unticks and adds.

**2.3 Statuses.** Condition: the object goes through stages.
- Full cycle (recommended when someone works on the object), list the statuses
- Simple: active and cancelled

**2.4 Notifications.** multiSelect of events the bot reports by itself: status change, new object for admin or staff, reminders, price drop, support reply, rating request.

**2.5 Data source.**
- The bot stores everything (recommended)
- External system (website, CRM, booking service)
- Spreadsheet
For an external system, ask which one and whether it has an API, phrased as behavior: "where do the products come from".

**2.6 Admin panel.** Condition: 1.3 has an admin. multiSelect: new objects with action buttons, today's list, catalog editing, statistics, broadcast, user bans.

**2.8 Loyalty rules.** Condition: 1.4 has bonuses, points or cashback.
- Accrual: percent of each order (ask the number) or fixed per visit
- Spending limit: up to N% of an order (recommended, ask N), any amount, or none
- When points arrive: after pickup or payment (recommended), at order time
- Expiry: never (recommended), after N months
- Purchases at the counter: staff adds them by the customer's code (recommended when there is a counter), or online orders only

**2.9 Timing rules.** Condition: pre-orders, bookings or delivery to a time.
- Minimum lead time: N minutes before the slot (ask N)
- Horizon: today only (recommended for takeaway), up to N days ahead
- Slot step: 5, 10, 15 or 30 minutes
- Working hours: from 1.9, or ask here
- Time zone: the business's city, never assumed

**2.7 Staff screens.** For every role besides user and admin: multiSelect of what it sees and does. Example for a master: own bookings for the day, confirm and reschedule, own schedule, days off.

## Round 3. General style

**3.1 Tone.** Preview: the same start screen in each tone.
- Neutral and businesslike, no direct address (recommended)
- Friendly, informal address
- Polite, formal address

**3.2 Density.** Preview: the start screen as a card, as a minimum, as a dashboard, built on this bot's data.
- Card: heading, field table, 2×2 buttons, footer (recommended)
- Minimum: one line and one main button, the rest as link buttons
- Dashboard: summary in one table row, counters in buttons

**3.3 Icon pack.** Condition: the owner has Premium. Preview: the same screen with each pack.
Before asking, list the icon roles the bot needs (scissors, calendar, cart...) and check each pack in `assets/icon-roles.json` or with `scripts/pack.py`. Recommend the pack that covers all roles; in each option, say what is missing. Fixed-color packs are offered only when their color matches the brand from 3.4. Never mix packs.

**3.4 Brand.**
- None, neutral Telegram look (recommended)
- Logo and color, will send
- Full brand book

**3.5 Images.**
- No images (recommended without the owner's own material)
- Own photos and illustrations, will send
- Object photos from the data source
- Generated images in an agreed style
For generation, run a mini round: references, then 3 sample images to choose from. Never generate images without this.

**3.6 Owner Premium.** Skip if `is_premium` is known from round 0.
- Yes
- No
- Not sure
With "No", build with the no-Premium rules and skip 3.3.

**3.7 Button colors.** Preview: one confirmation screen in each scheme.
- By meaning: green finishes, red cancels, the rest neutral (recommended)
- Blue for the main action on every screen, red for cancel
- Only red for destructive actions

## Round 4. Screen layouts

Ask only for screen types the bot has (from 1.4 and 2.1). Every fork gets a preview first.

**4.1 Start screen.** Preview 3-4 start screens matching 3.2: card, minimum, dashboard, menu list, collapsible "what the bot does", offer accent.

**4.2 Object card.**
- Heading with status and a field table (recommended, required for requests and orders)
- Photo, price, specs table
- One-row summary table
- Specs in a collapsible block
Photo options only if 3.5 has photos.

**4.3 Several photos.** Condition: objects have more than one photo.
- Slideshow (recommended)
- One main photo

**4.4 Object list.** Recommend buttons up to 8 items, a numbered table with paging above that.
- Link buttons, one per row, price and details in the label
- Numbered table and number buttons
- 2×N button grid
- Numbered list with sort links

**4.5 Groups in a list.** Condition: objects have categories. No recommendation: both first options are equally good.
- Collapsed groups with object buttons inside
- Expanded: subheadings and object buttons
- Category screen first, then the list

**4.6 Navigation.**
- Edit one message, Back and Home at the bottom (recommended)
- Mixed: steps by editing, results as new messages
- Every screen as a new message

**4.7 Confirmations.**
- Only irreversible actions (recommended)
- Everything with money or deletion
- None

**4.8 Search.** Condition: more than 20 objects.
- Results with highlighted matches and number buttons (recommended)
- Inline search via @bot
- No search

**4.9 Quantity.** Condition: objects can be ordered in quantity.
- Stepper row: "-", disabled "1 pc", "+" (recommended)
- Typing a number

**4.10 Notifications.** Preview: one notification in both forms.
- Full block: heading, field table, action buttons (recommended)
- One compact line with buttons

**4.11 AI answers.** Condition: the bot generates text.
- Streamed draft, then the final message
- Typing indicator, then the final message

**4.12 Date and time.** Condition: bookings, pickup or delivery to a time.
With people to choose (masters, couriers):
- Slot grid for one person, taken slots disabled, day paging (recommended)
- Free time table for everyone and an "Anyone, earliest" button
- Table to pick a person, then their slot grid
Without people (pickup, delivery):
- Quick buttons "In 15 min", "In 30 min", "In 45 min", then "Pick a time" with a slot grid (recommended)
- Slot grid only

## Round 5. Bot profile

**5.1 Name.** Asked in round 0. 3 options from the purpose plus "Other".

**5.2 Username.** Asked in round 0, permanent. 3 free options checked with `scripts/username.py`. For Premium owners, mention that a secondary username ending in `agent`, `ai`, `app`, or `game` is possible.

**5.3 Description and short description.** Description up to 512 characters, shown before Start; short description up to 120 characters, shown in the profile. Write 2 options each.
They are written for the bot's users: what the business is, where, what makes it different, when it works. Do not list bot features ("pick a master, reminders, rescheduling"); that reads like an LLM writing for a developer. Use only facts from 1.9. When users already know the business (internal tool, bot on a website), keep it short and say why they need this bot.

**5.4 Profile photo.**
- Owner's logo (recommended)
- None for now
- Generated in the agreed style (only with an agreed style)

**5.5 Commands.** multiSelect of commands with descriptions from 1.4. `/start` is not a question: it is always first in the menu ("Main menu"). Staff and admin commands are not in this list; they are set per staff chat with `BotCommandScopeChat`.

**5.6 Menu button.** Derived: commands list without a Mini App, Mini App launch when the Mini App is the main interface.

## Round 6. Summary

A table with three columns: decision, choice, source ("answer", "recommendation accepted", "derived from ..."). Under it, one line of Claude's technical decisions: hosting, storage, how the bot was created. Ask "Is everything right?" with "Start" and "Changes". On changes, return only to the affected questions.

## Never ask

- Programming language, framework, libraries.
- Serverless or server, database, hosting, webhook or polling.
- Code structure and file names.
- Anything already answered in this conversation or in the project's earlier decisions.
