# Rich messages reference

Checked against Bot API 10.4 (November 9, 2026). Source: https://core.telegram.org/bots/api#rich-messages. If the changelog shows a newer version, read it before building.

## Methods

**sendRichMessage** returns the sent Message.
- `chat_id` (required unless the message is an ephemeral reply to a callback query)
- `rich_message`: InputRichMessage (required)
- `message_thread_id`, `direct_messages_topic_id`, `business_connection_id`
- `ephemeral_message_parameters`: show the message to one user only
- `disable_notification`, `protect_content`, `allow_paid_broadcast`, `message_effect_id` (private chats)
- `reply_parameters`, `reply_markup` (works, but prefer buttons inside the message)
- If a block contains media, the bot needs the right to send media in that chat.

**editMessageText** with `rich_message` instead of `text` replaces the content of a message. This is how navigation works: `chat_id`, `message_id`, `rich_message`. Uploading new files is not supported when editing inline messages.

**sendRichMessageDraft** streams a temporary preview (about 30 seconds) to a private chat while text is generated.
- `chat_id` (private chat), `draft_id` (non-zero; the same id animates changes), `rich_message`
- `can_stop`: show a stop button; the bot gets `stopped_message_generation`
- `keep_on_stop`: keep the draft when stopped
- Direct uploads and uploads by URL are not supported in drafts.
- `<tg-thinking>Thinking...</tg-thinking>` works only in drafts.
- After the final step, persist the result with `sendRichMessage`.

## InputRichMessage

Exactly one of `html`, `markdown`, `blocks`.
- `html`: Rich HTML (used by this skill)
- `markdown`: GitHub-flavored Markdown plus HTML
- `blocks`: explicit InputRichBlock objects
- `media`: array of InputRichMessageMedia, referenced as `tg://photo?id=<id>`, `tg://video?id=`, `tg://document?id=`, `tg://audio?id=`
- `is_rtl`, `skip_entity_detection`

**InputRichMessageMedia**: `id` (1-64 chars, `A-Z a-z 0-9 _ -`) and `media` (InputMediaPhoto, InputMediaVideo, InputMediaAnimation, InputMediaAudio, InputMediaDocument, InputMediaVoiceNote). Only the file itself is used. To reuse an uploaded photo: `{"id": "hero", "media": {"type": "photo", "media": "<file_id>"}}` and `<img src="tg://photo?id=hero"/>`. A practical way to get a file_id: upload once with `sendPhoto`, store `photo[-1].file_id`, delete that message.

## Limits

- 32768 UTF-8 characters of text, including custom emoji alt text and formula source
- 500 blocks, counting nested blocks, list items, table rows, quotations, details
- 16 levels of nesting
- 50 media attachments
- 20 table columns
- Media only as separate blocks, only HTTP(S) URLs or `tg://` media links
- Table cells hold inline formatting only

## Rich HTML tags

Inline: `<b>`, `<i>`, `<u>`/`<ins>`, `<s>`/`<del>`, `<code>`, `<mark>`, `<sub>`, `<sup>`, `<tg-spoiler>`, `<a href>`, `<tg-emoji emoji-id="..">alt</tg-emoji>`, `<tg-time unix=".." format="wDT">fallback</tg-time>`, `<tg-math>`, `<tg-reference name>`.

Blocks:
- `<h1>`-`<h6>`, `<p>`, `<pre>`, `<pre><code class="language-x">`, `<footer>`, `<hr/>`
- `<ul>`, `<ol start type reversed>`, `<li value>`, checklists with `<li><input type="checkbox" checked>..</li>`
- `<blockquote>` with optional `<cite>`, `<blockquote expandable>`, `<aside>` (pull quote)
- `<img src>`, `<video src>`, `<audio src>`, `<tg-document src>`, optional `tg-spoiler` attribute on media
- `<figure>` with `<figcaption>` and `<cite>`
- `<tg-map lat long zoom/>`
- `<tg-collage>`, `<tg-slideshow>` with media and `<figcaption>`
- `<table bordered striped compact>` with `<caption>`, `<tr>`, `<th>`, `<td colspan rowspan align valign>`
- `<details open><summary>..</summary>..</details>` (body may contain blocks, including button rows)
- `<tg-math-block>`, `<a name>` anchors
- `<tg-button-row align="left|center|right">` with `<tg-button>` children

Named entities: only `&lt; &gt; &amp; &quot; &apos; &nbsp; &hellip; &mdash; &ndash; &lsquo; &rsquo; &ldquo; &rdquo;`; numeric entities work. Escape `<`, `>`, `&` in user data.

## Buttons

`<tg-button type=".." style="..">label</tg-button>`

| type | attributes |
|---|---|
| `callback_data` | `data` (1-64 bytes) |
| `url` | `url` (HTTP or `tg://`) |
| `web_app` | `url` (private chats only) |
| `login_url` | `url`, `forward-text`, `request-write-access` |
| `switch_inline_query` | `query` |
| `switch_inline_query_current_chat` | `query` |
| `switch_inline_query_chosen_chat` | `query`, `allow-user-chats`, `allow-bot-chats`, `allow-group-chats`, `allow-channel-chats` |
| `copy_text` | `text` |
| `disabled` | none; the button does nothing |

- `style`: `primary`, `success`, `danger`, or `link` (a borderless link; callback buttons only).
- Label: plain text, custom emoji (`<tg-emoji>`), and `<tg-time>` only.
- A row holds the buttons of one `<tg-button-row>`; buttons can also appear inline inside `<p>`.

## Classic inline keyboards (fallback)

`InlineKeyboardButton` also has `style` (`danger`, `success`, `primary`), `icon_custom_emoji_id` (needs owner Premium or a Fragment username), and `disabled`. Use them only when a rich message is not possible.

## Custom emoji

Allowed in messages the bot sends to private chats, groups and supergroups if the bot owner has Telegram Premium (or the bot has a Fragment username). Without it, `<tg-emoji>` falls back to its alt text, which looks broken; do not send custom emoji then.

## Related features worth using

- Ephemeral messages (`ephemeral_message_parameters`): a reply visible only to the user who pressed a button in a group.
- `date_time` entities and `<tg-time>`: dates shown in the reader's time zone.
- `copy_text` buttons for order numbers, codes, addresses.
- Managed bots (`KeyboardButtonRequestManagedBot`, `getManagedBotToken`) for services that create bots for their users.
