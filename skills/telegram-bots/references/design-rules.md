# Design rules

Rules come from side-by-side reviews of real bots and of generated variants. They cover the visual structure only; texts follow the interview answers.

## What good bots do

- A screen starts with a heading: icon, title, and a status after " · " ("Order #1042 · On the way").
- Structured data goes into a table of "field · value" rows, not into lines of text.
- Buttons sit inside the message, two per row; the main action of the screen gets its own row.
- Back and Home stay at the bottom, full width or as a pair.
- Counters go into button labels ("Users · 27") instead of separate screens.
- Service information goes into a footer or monospace (`<code>`) for ids and numbers.
- Links are URL buttons, never raw URLs in text.
- The command menu is filled, every command has a description.
- One icon pack, one style, on every screen.

## What bad bots do

- A reply keyboard with many buttons as the main menu.
- Regular colorful emoji used as icons, mixed with each other.
- Filler lines: "Choose a button below", "If you have questions, we are always happy to help".
- A sticker or greeting sent as a separate message.
- Commands listed as text instead of buttons.
- A wall of text above a single button.
- Button labels longer than about 14 characters in a two-button row: they get cut ("Trusted sour...").

## Screen patterns

Every pattern below was approved in review. HTML is the `html` field of `InputRichMessage`; `{icon:role}` stands for a `<tg-emoji>` from the chosen pack.

### Object card (required for requests, orders, bookings)
```html
<h3>{icon:box} Order #1042 · On the way</h3>
<table bordered compact>
<tr><td>{icon:box} Items</td><td><b>Aero headphones, 1 pc</b></td></tr>
<tr><td>{icon:coin} Total</td><td><b>12 990 ₽</b></td></tr>
<tr><td>{icon:clock} Delivery</td><td><b><tg-time unix="1795000000" format="wDT">today</tg-time></b></td></tr>
</table>
<tg-button-row><tg-button type="callback_data" data="track" style="primary">{icon:pin} Track</tg-button><tg-button type="callback_data" data="chat">{icon:chat} Contact</tg-button></tg-button-row>
<tg-button-row><tg-button type="callback_data" data="cancel" style="danger">{icon:cross} Cancel order</tg-button></tg-button-row>
```

### Admin request
Heading with status, field table, then "In progress" (primary), "Done" (success), "Reject" (danger), "Comment" (neutral) in two rows.

### Product card
Photo block, `<h3>` name, `<h2>` price, compact specs table, "Add to cart" (success) on its own row, Back and Favorites below. Variants that also work: specs in `<details>`, one-row summary table with price, stock and rating.

### Several photos
`<tg-slideshow>` with a `<figcaption>`. Collages were rejected for product screens.

### Quantity stepper (required wherever quantity is chosen)
```html
<tg-button-row><tg-button type="callback_data" data="minus">-</tg-button><tg-button type="disabled">1 pc</tg-button><tg-button type="callback_data" data="plus">+</tg-button></tg-button-row>
<tg-button-row><tg-button type="callback_data" data="cart" style="success">{icon:plus} Add to cart · 12 990 ₽</tg-button></tg-button-row>
```

### Old and new price
`<p><s>15 990 ₽</s> <mark><b>12 990 ₽</b></mark></p>` and a line with the offer deadline.

### Long review or text
`<blockquote expandable>` with `<cite>`.

### Lists
- Up to 8 items: link buttons (`style="link"`), one per row, `align="left"`, details in the label.
- More: numbered table (`<table bordered striped compact>`), a row of number buttons, paging.
- Categories: collapsed `<details>` with item buttons inside, or `<h4>` subheadings with item buttons; ask the owner which.
- Paging: `‹`, disabled `1 / 10`, `›`.

### Search results
`<h3>` with the query, `<ul>` with matches wrapped in `<mark>`, footer "Found 3", number buttons.

### Filters
Field table with current filter values, a button per filter, then "Reset" (danger) and "Show 12" (success).

### Order stages
`<ul>` with `<input type="checkbox" checked>` items and times, footer with the expected time.

### Delivery or location
`<figure><tg-map lat=".." long=".." zoom="14"/><figcaption>..</figcaption></figure>`.

### Tracking number
`<pre>` with the number, a `copy_text` button and a URL button.

### Result of an action (required)
```html
<h3>{icon:check} Order placed</h3>
<p>Number <b>#1042</b>, delivery today before 22:00.</p>
<tg-button-row><tg-button type="callback_data" data="order" style="primary">{icon:box} Open order</tg-button><tg-button type="callback_data" data="home">{icon:home} Home</tg-button></tg-button-row>
```

### Destructive confirmation
Heading with the question, one line with the object, "Delete" (danger) next to a neutral "Cancel".

### Error
Heading, the reason in `<blockquote>` with `<cite>` for a code, "Retry" (primary) on its own row, fallback actions below.

### Empty state
Heading, one line, one button out of the dead end.

### Receipt (required after payment)
Heading with the amount, field table (order, method, bonus), footer, `copy_text` button with the receipt number.

### Warning with details (required)
Heading, one line, `<details>` with the explanation, action buttons.

### Rating (required after a service)
Row of buttons 1-5, the best one `success`, then "Write a review".

### AI answer
Optional: stream with `sendRichMessageDraft` (first a `<tg-thinking>` step), then send the final message with `sendRichMessage`.

### Single choice (size, option)
The chosen option is a `disabled` button, the others are callback buttons, all in one row: `S · 250` (callback), `M · 290` (disabled), `L · 330` (callback). Works with and without Premium.

### Multiple choice (add-ons, filters)
Each option is a link-style button, one per row; a chosen option starts with `✓ ` in its label ("✓ Caramel syrup · +50 ₽"). Here `✓` carries state, so it is allowed without Premium too. A "Done" button (primary) closes the list.

### Text input (comment, amount, code)
Edit the current screen into a prompt: heading, one line saying what to send, an example in `<code>`, and "Cancel". When the user's message arrives, delete it (`deleteMessage`), validate it, and edit the same screen back with the value applied, or with the error in a `<blockquote>`. Never leave the prompt and the answer as two loose messages.

### Staff roles
- Invite staff with a one-time deep link `https://t.me/<bot>?start=inv_<token>`; the token is single-use and expires.
- Staff get their own home row ("Orders", "Barista panel") on the start screen and their own commands via `setMyCommands` with `BotCommandScopeChat`.
- New objects for staff arrive as a full block with action buttons (see "Admin request").

### Command menu
`/start` first ("Main menu"), then the public commands from the interview. Staff commands only in per-chat scopes.

### Numbers
Format money and points with a thin rule: no sign for zero ("Points · 0"), `+` only for positive changes, thousands separated by a space, currency after the number ("12 990 ₽").

## Rejected patterns

- A big pull quote (`<aside>`) as a final status: use a heading instead.
- A one-line notification: use a full block with a field table.
- An order table with several columns and a colspan total row: use "field · value" rows.
- Collages for product photos.
- Generated banners and schematic pictures.
- Fixed-color icon packs that do not match the brand.

## Without Premium

Custom emoji are unavailable, so the layout must carry the structure by itself.
- Keep headings, tables, button rows and colors exactly as with Premium.
- Remove icons from headings and buttons; do not replace them with regular emoji.
- In tables, mark field names with `›`. Use `·` as a separator. `✓` marks chosen items in multiple choice; otherwise `✓` and `✕` appear only inside text, never as decorations.
- Paging, steppers and footers stay the same.
- The list screen with a numbered table, `›` markers and paging was approved; other no-Premium screens still need review, so show the owner previews.
