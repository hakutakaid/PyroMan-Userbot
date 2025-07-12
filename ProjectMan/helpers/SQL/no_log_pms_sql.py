import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_no_log_pms_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'no_log_pms' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS no_log_pms (
                    chat_id INTEGER PRIMARY KEY
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'no_log_pms' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'no_log_pms' table: {e}")
            return False
    return False

if DB_AVAILABLE:
    create_no_log_pms_table()
else:
    LOGGER(__name__).error("Database not available when loading no_log_pms.py.")

---

## PM Logging Approval Functions

def is_approved(chat_id: int) -> bool | None:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot check approval status.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT 1 FROM no_log_pms WHERE chat_id = ?", (chat_id,))
            row = cursor.fetchone()
            return row is not None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to check approval status for chat {chat_id}: {e}")
            return None
    return None

def approve(chat_id: int):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot approve chat.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR IGNORE INTO no_log_pms (chat_id) VALUES (?)", (chat_id,))
            conn.commit()
            LOGGER(__name__).info(f"Chat {chat_id} has been approved (if not already).")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to approve chat {chat_id}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to approve chat.")

def disapprove(chat_id: int):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot disapprove chat.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM no_log_pms WHERE chat_id = ?", (chat_id,))
            if cursor.rowcount > 0:
                conn.commit()
                LOGGER(__name__).info(f"Chat {chat_id} has been disapproved.")
            else:
                LOGGER(__name__).info(f"Chat {chat_id} not found in approved list.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to disapprove chat {chat_id}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to disapprove chat.")
