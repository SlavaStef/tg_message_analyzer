import logging
from telethon import events
from db import load_chats, load_keywords
from config import TARGET

logger = logging.getLogger(__name__)

def register_monitor_handler(client, conn) -> None:
    @client.on(events.NewMessage())
    async def handler(event):
        # Load configuration
        monitored_chats = load_chats(conn)
        monitored_keywords = load_keywords(conn)

        # Prepare filters for IDs and usernames
        ids = {int(c) for c in monitored_chats if c.lstrip('-').isdigit()}
        names = {c.lower().lstrip('@').split('/')[-1] for c in monitored_chats if not c.lstrip('-').isdigit()}

        # Extract event chat identifiers
        chat_id = event.chat_id
        chat_user = (event.chat.username or '').lower() if event.chat else ''

        # Skip messages not in monitored chats
        if chat_id not in ids and chat_user not in names:
            return

        # Get message text
        message_text = event.message.message or ''
        text_lower = message_text.lower()

        # Check for keyword matches
        for kw in monitored_keywords:
            if kw in text_lower:
                logger.info("Detected keyword '%s' in '%s' (message %d)",
                            kw,
                            event.chat.title or chat_user or str(chat_id),
                            event.message.id)

                # Build a clickable link if username available
                link = f"https://t.me/{chat_user}/{event.message.id}" if chat_user else ''

                # Format notification
                note = (
                    f"🔎 Keyword '{kw}' detected in '{event.chat.title or chat_user or chat_id}':"f"{message_text}{link}"
                )

                # Forward to configured TARGET
                try:
                    await client.send_message(TARGET, note)
                    logger.debug("Notification forwarded to %s", TARGET)
                except Exception as e:
                    logger.error("Failed to forward notification to %s: %s", TARGET, e)

                break