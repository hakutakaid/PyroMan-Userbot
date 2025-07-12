import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_gmute_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'gmute' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gmute (
                    sender TEXT PRIMARY KEY
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'gmute' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'gmute' table: {e}")
            return False
    return False

if DB_AVAILABLE:
    create_gmute_table()
else:
    LOGGER(__name__).error("Database not available when loading gmute.py.")

---

## Global Mute Management Functions

def is_gmuted(sender: int | str) -> bool | None:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot check gmute status.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT 1 FROM gmute WHERE sender = ?", (str(sender),))
            row = cursor.fetchone()
            return row is not None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to check gmute status for {sender}: {e}")
            return None
    return None

def gmuted_users() -> list[str] | None:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve gmuted users list.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT sender FROM gmute")
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to retrieve gmuted users list: {e}")
            return None
    return None

def gmute(sender: int | str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot perform gmute.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR IGNORE INTO gmute (sender) VALUES (?)", (str(sender),))
            conn.commit()
            LOGGER(__name__).info(f"Sender {sender} has been gmuted (if not already).")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to gmute sender {sender}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to gmute.")

def ungmute(sender: int | str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot perform ungmute.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM gmute WHERE sender = ?", (str(sender),))
            if cursor.rowcount > 0:
                conn.commit()
                LOGGER(__name__).info(f"Sender {sender} has been ungmuted.")
            else:
                LOGGER(__name__).info(f"Sender {sender} not found in the gmute list.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to ungmute sender {sender}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to ungmute.")