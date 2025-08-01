# ProjectMan/helpers/SQL/globals.py

import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_gvar_table():
    """Creates the 'gvar' table if it doesn't already exist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'gvar' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gvar (
                    key TEXT PRIMARY KEY NOT NULL,
                    value TEXT
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'gvar' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'gvar' table: {e}")
            return False
    return False

def addgvar(key: str, value: str):
    """Adds or updates a global variable."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot set gvar.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR REPLACE INTO gvar (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            LOGGER(__name__).info(f"Global variable '{key}' set to '{value}'.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to set gvar '{key}': {e}")

def gvarstatus(key: str) -> str | None:
    """Gets the value of a global variable."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot get gvar status.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT value FROM gvar WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get gvar status for '{key}': {e}")
            return None
    return None

def delgvar(key: str) -> bool:
    """Deletes a global variable."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot delete gvar.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM gvar WHERE key = ?", (key,))
            conn.commit()
            if cursor.rowcount > 0:
                LOGGER(__name__).info(f"Global variable '{key}' deleted successfully.")
                return True
            else:
                LOGGER(__name__).info(f"Global variable '{key}' not found, no deletion performed.")
                return False
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to delete gvar '{key}': {e}")
            return False
    return False

def get_botlog_chat_id() -> int | str | None:
    """Retrieves BOTLOG_CHATID from global variables."""
    chat_id_str = gvarstatus("BOTLOG_CHATID")
    if chat_id_str:
        try:
            return int(chat_id_str)
        except ValueError:
            return chat_id_str
    return None

def set_botlog_chat_id(chat_id: int | str):
    """Sets BOTLOG_CHATID in global variables."""
    addgvar("BOTLOG_CHATID", str(chat_id))

if DB_AVAILABLE:
    create_gvar_table()
else:
    LOGGER(__name__).error("Database not available when loading globals.py.")
