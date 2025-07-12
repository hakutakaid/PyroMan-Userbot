import threading
import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_whitelist_users_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'pmapprove' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pmapprove (
                    user_id TEXT PRIMARY KEY,
                    username TEXT
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'pmapprove' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'pmapprove' table: {e}")
            return False
    return False

def create_req_users_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'getpmapprove' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS getpmapprove (
                    user_id TEXT PRIMARY KEY,
                    username TEXT
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'getpmapprove' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'getpmapprove' table: {e}")
            return False
    return False

if DB_AVAILABLE:
    create_whitelist_users_table()
    create_req_users_table()
else:
    LOGGER(__name__).error("Database not available when loading pmapprove_sql.py.")



## PM Whitelist and Request Management

INSERTION_LOCK = threading.RLock()

def set_whitelist(user_id: int | str, username: str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot set whitelist.")
        return

    with INSERTION_LOCK:
        conn, cursor = get_db_connection()
        if conn and cursor:
            try:
                cursor.execute("INSERT OR REPLACE INTO pmapprove (user_id, username) VALUES (?, ?)",
                               (str(user_id), str(username)))
                conn.commit()
                LOGGER(__name__).info(f"Whitelist user {user_id} ({username}) set/updated.")
            except sqlite3.Error as e:
                LOGGER(__name__).error(f"Failed to set whitelist for user {user_id}: {e}")
        else:
            LOGGER(__name__).error("Invalid database connection when trying to set whitelist.")

def del_whitelist(user_id: int | str) -> bool:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot delete whitelist.")
        return False

    with INSERTION_LOCK:
        conn, cursor = get_db_connection()
        if conn and cursor:
            try:
                cursor.execute("DELETE FROM pmapprove WHERE user_id = ?", (str(user_id),))
                if cursor.rowcount > 0:
                    conn.commit()
                    LOGGER(__name__).info(f"Whitelist user {user_id} deleted.")
                    return True
                else:
                    LOGGER(__name__).info(f"Whitelist user {user_id} not found for deletion.")
                    return False
            except sqlite3.Error as e:
                LOGGER(__name__).error(f"Failed to delete whitelist for user {user_id}: {e}")
                return False
        else:
            LOGGER(__name__).error("Invalid database connection when trying to delete whitelist.")
            return False

def get_whitelist(user_id: int | str) -> str:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot get whitelist.")
        return ""

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT username FROM pmapprove WHERE user_id = ?", (str(user_id),))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return ""
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get whitelist for user {user_id}: {e}")
            return ""
    return ""

def set_req(user_id: int | str, username: str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot set PM request.")
        return

    with INSERTION_LOCK:
        conn, cursor = get_db_connection()
        if conn and cursor:
            try:
                cursor.execute("INSERT OR REPLACE INTO getpmapprove (user_id, username) VALUES (?, ?)",
                               (str(user_id), str(username)))
                conn.commit()
                LOGGER(__name__).info(f"PM request user {user_id} ({username}) set/updated.")
            except sqlite3.Error as e:
                LOGGER(__name__).error(f"Failed to set PM request for user {user_id}: {e}")
        else:
            LOGGER(__name__).error("Invalid database connection when trying to set PM request.")

def get_req(user_id: int | str) -> str:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot get PM request.")
        return ""

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT username FROM getpmapprove WHERE user_id = ?", (str(user_id),))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return ""
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get PM request for user {user_id}: {e}")
            return ""
    return ""
