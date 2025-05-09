import sqlite3
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    '''
    Establish and return a new SQLite database connection.

    Returns:
        sqlite3.Connection: Database connection object.
    '''
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db(conn: sqlite3.Connection) -> None:
    '''
    Initialize database tables if they do not exist.

    Args:
        conn (sqlite3.Connection): Active database connection.
    '''
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()

def load_chats(conn: sqlite3.Connection) -> list[str]:
    '''
    Retrieve the list of monitored chats from the database.

    Args:
        conn (sqlite3.Connection): Active database connection.

    Returns:
        list[str]: List of chat identifiers.
    '''
    cursor = conn.cursor()
    cursor.execute("SELECT chat FROM chats")
    return [row[0] for row in cursor.fetchall()]

def load_keywords(conn: sqlite3.Connection) -> set[str]:
    '''
    Retrieve the set of monitored keywords from the database.

    Args:
        conn (sqlite3.Connection): Active database connection.

    Returns:
        set[str]: Set of keywords.
    '''
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM keywords")
    return {row[0] for row in cursor.fetchall()}

def add_chat(conn: sqlite3.Connection, chat: str) -> None:
    '''
    Add a new chat to the database if not already present.

    Args:
        conn (sqlite3.Connection): Active database connection.
        chat (str): Chat identifier to add.
    '''
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO chats(chat) VALUES(?)", (chat,))
    conn.commit()

def remove_chat(conn: sqlite3.Connection, chat: str) -> None:
    '''
    Remove a chat from the database.

    Args:
        conn (sqlite3.Connection): Active database connection.
        chat (str): Chat identifier to remove.
    '''
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chats WHERE chat=?", (chat,))
    conn.commit()

def add_keyword(conn: sqlite3.Connection, keyword: str) -> None:
    '''
    Add a new keyword to the database if not already present.

    Args:
        conn (sqlite3.Connection): Active database connection.
        keyword (str): Keyword to add.
    '''
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO keywords(keyword) VALUES(?)", (keyword.lower(),))
    conn.commit()

def remove_keyword(conn: sqlite3.Connection, keyword: str) -> None:
    '''
    Remove a keyword from the database.

    Args:
        conn (sqlite3.Connection): Active database connection.
        keyword (str): Keyword to remove.
    '''
    cursor = conn.cursor()
    cursor.execute("DELETE FROM keywords WHERE keyword=?", (keyword.lower(),))
    conn.commit()