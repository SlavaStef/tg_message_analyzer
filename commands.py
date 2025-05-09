import logging
from telethon import events, Button
from telethon.tl.custom import Message
from telethon.errors.rpcerrorlist import MessageNotModifiedError
from db import (
    add_chat,
    remove_chat,
    add_keyword,
    remove_keyword,
    load_chats,
    load_keywords
)

logger = logging.getLogger(__name__)
_USER_STATE: dict[int, str] = {}

# Inline menu button definitions
_MENU_BUTTONS = [
    [Button.inline("➕ Add Chat", b"menu:add_chat"), Button.inline("➖ Remove Chat", b"menu:rm_chat")],
    [Button.inline("➕ Add Keyword", b"menu:add_kw"), Button.inline("➖ Remove Keyword", b"menu:rm_kw")],
    [Button.inline("📋 List Chats", b"menu:list_chats"), Button.inline("📋 List Keywords", b"menu:list_kw")]
]

async def show_menu(event: Message) -> None:
    """
    Send the main menu with inline buttons.
    """
    logger.debug("Showing main menu to user %s", event.sender_id)
    await event.respond(
        "Please select an action:",
        buttons=_MENU_BUTTONS
    )

# Pattern for slash commands
COMMAND_PATTERN = r'^/(addchat|rmchat|addkw|rmkw|listchats|listkw)(?:\s+(.+))?$'

def register_slash_commands(client, conn) -> None:
    """
    Register slash command handlers for chats and keywords management.
    Supports: /addchat, /rmchat, /addkw, /rmkw, /listchats, /listkw
    """
    @client.on(events.NewMessage(pattern=COMMAND_PATTERN))
    async def slash_handler(event):
        cmd = event.pattern_match.group(1)
        arg = event.pattern_match.group(2) or ''
        arg = arg.strip()

        if cmd == 'addchat' and arg:
            add_chat(conn, arg)
            return await event.reply(f"✅ Chat added: {arg}")

        if cmd == 'rmchat' and arg:
            remove_chat(conn, arg)
            return await event.reply(f"🗑️ Chat removed: {arg}")

        if cmd == 'addkw' and arg:
            add_keyword(conn, arg)
            return await event.reply(f"✅ Keyword added: {arg}")

        if cmd == 'rmkw' and arg:
            remove_keyword(conn, arg)
            return await event.reply(f"🗑️ Keyword removed: {arg}")

        if cmd == 'listchats':
            chats = load_chats(conn)
            text = "Monitored chats:\n" + "\n".join(chats) if chats else "No chats configured."
            return await event.reply(text)

        if cmd == 'listkw':
            kws = sorted(load_keywords(conn))
            text = "Monitored keywords:\n" + "\n".join(kws) if kws else "No keywords configured."
            return await event.reply(text)

        # Unknown command or missing argument
        await event.reply("❓ Unknown command or missing argument.")


def register_commands(client, conn) -> None:
    """
    Register all command handlers (slash commands + inline menu flows).
    """
    # 1) Slash commands
    register_slash_commands(client, conn)

    # 2) Inline /menu handler
    @client.on(events.NewMessage(pattern=r'^/(start|menu)$'))
    async def start_handler(event):
        await show_menu(event)

    # 3) Inline button callbacks
    @client.on(events.CallbackQuery)
    async def callback_handler(event):
        user_id = event.sender_id
        data = event.data.decode('utf-8')
        parts = data.split(':', 2)
        prefix, action = parts[0], parts[1] if len(parts) > 1 else None

        # Menu actions
        if prefix == 'menu':
            if action == 'add_chat':
                _USER_STATE[user_id] = 'add_chat'
                return await event.edit("🔹 Send the chat username or ID to add:")

            if action == 'rm_chat':
                chats = load_chats(conn)
                buttons = [Button.inline(c, f"select:rm_chat:{c}") for c in chats] or [Button.inline("No chats", b"noop")]
                try:
                    await event.edit("🔹 Select a chat to remove:", buttons=buttons)
                except MessageNotModifiedError:
                    pass
                return

            if action == 'add_kw':
                _USER_STATE[user_id] = 'add_kw'
                return await event.edit("🔹 Send the keyword to add:")

            if action == 'rm_kw':
                keywords = sorted(load_keywords(conn))
                buttons = [Button.inline(k, f"select:rm_kw:{k}") for k in keywords] or [Button.inline("No keywords", b"noop")]
                try:
                    await event.edit("🔹 Select a keyword to remove:", buttons=buttons)
                except MessageNotModifiedError:
                    pass
                return

            if action == 'list_chats':
                chats = load_chats(conn)
                text = "Monitored chats:\n" + "\n".join(chats) if chats else "No chats configured."
                return await event.answer(text, alert=True)

            if action == 'list_kw':
                keywords = sorted(load_keywords(conn))
                text = "Monitored keywords:\n" + "\n".join(keywords) if keywords else "No keywords configured."
                return await event.answer(text, alert=True)

        # Selection callbacks
        if prefix == 'select' and len(parts) == 3:
            _, act, item = parts
            if act == 'rm_chat':
                remove_chat(conn, item)
                return await event.edit(f"🗑️ Removed chat: {item}")
            if act == 'rm_kw':
                remove_keyword(conn, item)
                return await event.edit(f"🗑️ Removed keyword: {item}")

        # Fallback: acknowledge
        await event.answer()

    # 4) Handle text input after prompts
    @client.on(events.NewMessage())
    async def input_handler(event):
        user_id = event.sender_id
        state = _USER_STATE.pop(user_id, None)
        if not state:
            return
        value = event.text.strip()

        if state == 'add_chat':
            add_chat(conn, value)
            await event.reply(f"✅ Chat added: {value}")
        elif state == 'add_kw':
            add_keyword(conn, value)
            await event.reply(f"✅ Keyword added: {value}")

        await show_menu(event)