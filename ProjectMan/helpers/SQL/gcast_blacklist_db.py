# ProjectMan/helpers/SQL/gcast_blacklist_db.py

import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_gcast_blacklist_table():
    """Creates the 'gcast_blacklist' table if it doesn't already exist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'gcast_blacklist' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gcast_blacklist (
                    chat_id INTEGER PRIMARY KEY NOT NULL
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'gcast_blacklist' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'gcast_blacklist' table: {e}")
            return False
    return False

def add_chat_to_blacklist(chat_id: int) -> bool:
    """Adds a chat ID to the GCAST blacklist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot add chat to blacklist.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR IGNORE INTO gcast_blacklist (chat_id) VALUES (?)", (chat_id,))
            conn.commit()
            if cursor.rowcount > 0:
                LOGGER(__name__).info(f"Chat {chat_id} added to GCAST blacklist.")
                return True
            else:
                LOGGER(__name__).info(f"Chat {chat_id} is already in GCAST blacklist.")
                return False
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to add chat {chat_id} to GCAST blacklist: {e}")
            return False
    return False

def remove_chat_from_blacklist(chat_id: int) -> bool:
    """Removes a chat ID from the GCAST blacklist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot remove chat from blacklist.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM gcast_blacklist WHERE chat_id = ?", (chat_id,))
            conn.commit()
            if cursor.rowcount > 0:
                LOGGER(__name__).info(f"Chat {chat_id} removed from GCAST blacklist.")
                return True
            else:
                LOGGER(__name__).info(f"Chat {chat_id} not found in GCAST blacklist.")
                return False
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to remove chat {chat_id} from GCAST blacklist: {e}")
            return False
    return False

def get_gcast_blacklist() -> list[int]:
    """Retrieves all chat IDs from the GCAST blacklist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve GCAST blacklist.")
        return []

    conn, cursor = get_db_connection()
    blacklist = []
    if conn and cursor:
        try:
            cursor.execute("SELECT chat_id FROM gcast_blacklist")
            rows = cursor.fetchall()
            blacklist = [row[0] for row in rows]
            LOGGER(__name__).info(f"Retrieved {len(blacklist)} chats from GCAST blacklist.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to retrieve GCAST blacklist: {e}")
    return blacklist

# Call table creation function when the module is loaded
if DB_AVAILABLE:
    create_gcast_blacklist_table()
else:
    LOGGER(__name__).error("Database not available when loading gcast_blacklist_db.py.")