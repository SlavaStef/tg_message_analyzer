import logging
import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, SESSION_NAME
from db import get_connection, init_db
from commands import register_commands
from handlers import register_monitor_handler

def setup_logging() -> None:
    '''
    Configure root logger for the application.
    '''
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def main() -> None:
    '''
    Main function: initialize components and start the Telegram client.
    '''
    setup_logging()
    logger = logging.getLogger(__name__)

    # Initialize database connection and schema
    conn = get_connection()
    init_db(conn)

    # Initialize and configure Telegram client
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    register_commands(client, conn)
    register_monitor_handler(client, conn)

    # Start the client and enter message loop
    client.start()
    logger.info("🚀 Bot started and monitoring chats...")
    client.run_until_disconnected()

if __name__ == "__main__":
    main()