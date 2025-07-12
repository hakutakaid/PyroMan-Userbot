import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

try:
    from config import PM_LIMIT
except ImportError:
    PM_LIMIT = 3

warns = PM_LIMIT

def create_permitted_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'permitted' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permitted (
                    user_id INTEGER PRIMARY KEY NOT NULL,
                    warning INTEGER NOT NULL DEFAULT 0
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Table 'permitted' created or already exists.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to create 'permitted' table: {e}")
            return False
    return False

if DB_AVAILABLE:
    create_permitted_table()
else:
    LOGGER(__name__).error("Database not available when loading pmpermit_sql.py.")



## Functions

def get_user_warning_status(userid: int) -> int | None:
    if not DB_AVAILABLE:
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT warning FROM permitted WHERE user_id = ?", (userid,))
            row = cursor.fetchone()
            return row[0] if row else None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get warning status for user {userid}: {e}")
            return None
    return None

def givepermit(userid: int):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot give permit.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                cursor.execute("UPDATE permitted SET warning = -1 WHERE user_id = ?", (userid,))
                LOGGER(__name__).info(f"User {userid} permit updated to -1.")
            else:
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, -1))
                LOGGER(__name__).info(f"User {userid} added with permit -1.")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to give permit to user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to give permit.")

def checkpermit(userid: int) -> bool:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot check permit. Defaulting to True.")
        return True

    current_warning = get_user_warning_status(userid)

    if current_warning is not None:
        if current_warning == -1:
            return True
        elif current_warning == warns:
            return False
        else:
            return True
    else:
        return True

def blockuser(userid: int):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot block user.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                cursor.execute("UPDATE permitted SET warning = ? WHERE user_id = ?", (warns, userid))
                LOGGER(__name__).info(f"User {userid} warning updated to {warns} (blocked).")
            else:
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, warns))
                LOGGER(__name__).info(f"User {userid} added with {warns} warnings (blocked).")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to block user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to block user.")

def getwarns(userid: int) -> int | str:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot get warns. Returning 'USER DON'T EXISTS'.")
        return "USER DON'T EXISTS"

    warning_count = get_user_warning_status(userid)
    if warning_count is not None:
        return warning_count
    else:
        return "USER DON'T EXISTS"

def addwarns(userid: int):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot add warns.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                cursor.execute("UPDATE permitted SET warning = warning + 1 WHERE user_id = ?", (userid,))
                LOGGER(__name__).info(f"User {userid} warning incremented.")
            else:
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, 1))
                LOGGER(__name__).info(f"User {userid} added with 1 warning.")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to add warn to user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to add warns.")

def allallowed() -> list[int]:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve allowed users.")
        return []

    conn, cursor = get_db_connection()
    allowed_users_list = []
    if conn and cursor:
        try:
            cursor.execute("SELECT user_id FROM permitted WHERE warning = -1")
            rows = cursor.fetchall()
            allowed_users_list = [row[0] for row in rows]
            LOGGER(__name__).info(f"Retrieved {len(allowed_users_list)} allowed users.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get all allowed users: {e}")
    return allowed_users_list

def allblocked() -> list[int]:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve blocked users.")
        return []

    conn, cursor = get_db_connection()
    blocked_users_list = []
    if conn and cursor:
        try:
            cursor.execute("SELECT user_id FROM permitted WHERE warning = ?", (warns,))
            rows = cursor.fetchall()
            blocked_users_list = [row[0] for row in rows]
            LOGGER(__name__).info(f"Retrieved {len(blocked_users_list)} blocked users.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get all blocked users: {e}")
    return blocked_users_list

def inwarns() -> list[int]:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve users in warns.")
        return []

    conn, cursor = get_db_connection()
    in_warns_list = []
    if conn and cursor:
        try:
            cursor.execute("SELECT user_id FROM permitted WHERE warning > -1 AND warning < ?", (warns,))
            rows = cursor.fetchall()
            in_warns_list = [row[0] for row in rows]
            LOGGER(__name__).info(f"Retrieved {len(in_warns_list)} users in warning status.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get users in warns: {e}")
    return in_warns_list
