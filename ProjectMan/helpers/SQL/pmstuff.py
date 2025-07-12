import sqlite3

# Assume ProjectMan.helpers.SQL is already initialized and provides the DB connection
# and LOGGER.
from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

# Assume PM_LIMIT is defined in config.py
# Example placeholder if config is not available for testing:
try:
    from config import PM_LIMIT
except ImportError:
    PM_LIMIT = 3 # Default warning limit if config.py isn't found

warns = PM_LIMIT  # max number of warning for a user


def create_permitted_table():
    """Creates the 'permitted' table if it doesn't already exist."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot create 'permitted' table.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS permitted (
                    user_id INTEGER PRIMARY KEY NOT NULL, -- BigInteger becomes INTEGER
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

# Call the table creation function when the module is loaded
if DB_AVAILABLE:
    create_permitted_table()
else:
    LOGGER(__name__).error("Database not available when loading pmpermit_sql.py.")

---

## Functions

def get_user_warning_status(userid: int) -> int | None:
    """
    Helper function to get a user's warning count.
    Returns the warning count (int) or None if the user is not in the DB or DB error occurs.
    """
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
    """
    Grants a permit to the user by setting their warning count to -1.
    If the user doesn't exist, they are added.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot give permit.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                # User exists, update their warning
                cursor.execute("UPDATE permitted SET warning = -1 WHERE user_id = ?", (userid,))
                LOGGER(__name__).info(f"User {userid} permit updated to -1.")
            else:
                # User doesn't exist, add them with warning -1
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, -1))
                LOGGER(__name__).info(f"User {userid} added with permit -1.")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to give permit to user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to give permit.")


def checkpermit(userid: int) -> bool:
    """
    Checks if a user is permitted (-1 warning) or not blocked (not at max warns).
    Returns True if permitted, False if blocked (at max warns), or True by default if not in DB.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot check permit. Defaulting to True.")
        return True # Default to True if DB is unavailable

    current_warning = get_user_warning_status(userid)

    if current_warning is not None:
        if current_warning == -1:
            return True # Permitted
        elif current_warning == warns:
            return False # Blocked (at max warns)
        else:
            # User exists, but not explicitly permitted or blocked, treat as not blocked
            return True
    else:
        # User doesn't exist in DB, treat as not blocked
        return True


def blockuser(userid: int):
    """
    Blocks a user by setting their warning count to the maximum (warns).
    If the user doesn't exist, they are added with max warns.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot block user.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                # User exists, update their warning
                cursor.execute("UPDATE permitted SET warning = ? WHERE user_id = ?", (warns, userid))
                LOGGER(__name__).info(f"User {userid} warning updated to {warns} (blocked).")
            else:
                # User doesn't exist, add them with max warns
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, warns))
                LOGGER(__name__).info(f"User {userid} added with {warns} warnings (blocked).")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to block user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to block user.")


def getwarns(userid: int) -> int | str:
    """
    Gets the warning count of a specific user.
    Returns the warning count (int) or "USER DON'T EXISTS" if not found.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot get warns. Returning 'USER DON'T EXISTS'.")
        return "USER DON'T EXISTS"

    warning_count = get_user_warning_status(userid)
    if warning_count is not None:
        return warning_count
    else:
        return "USER DON'T EXISTS"


def addwarns(userid: int):
    """
    Increments a user's warning count by 1. If the user doesn't exist, they are added with 1 warning.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot add warns.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            current_warning = get_user_warning_status(userid)
            if current_warning is not None:
                # User exists, increment warning
                cursor.execute("UPDATE permitted SET warning = warning + 1 WHERE user_id = ?", (userid,))
                LOGGER(__name__).info(f"User {userid} warning incremented.")
            else:
                # User doesn't exist, add with 1 warning
                cursor.execute("INSERT INTO permitted (user_id, warning) VALUES (?, ?)", (userid, 1))
                LOGGER(__name__).info(f"User {userid} added with 1 warning.")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to add warn to user {userid}: {e}")
    else:
        LOGGER(__name__).error("Invalid database connection when trying to add warns.")


def allallowed() -> list[int]:
    """
    Retrieves a list of user IDs who are currently permitted (-1 warning).
    """
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
    """
    Retrieves a list of user IDs who are currently blocked (at max warns).
    """
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
    """
    Retrieves a list of user IDs who are currently in warning status (warning > -1 and < warns).
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database not available, cannot retrieve users in warns.")
        return []

    conn, cursor = get_db_connection()
    in_warns_list = []
    if conn and cursor:
        try:
            # SQLite's boolean logic for AND is straightforward
            cursor.execute("SELECT user_id FROM permitted WHERE warning > -1 AND warning < ?", (warns,))
            rows = cursor.fetchall()
            in_warns_list = [row[0] for row in rows]
            LOGGER(__name__).info(f"Retrieved {len(in_warns_list)} users in warning status.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Failed to get users in warns: {e}")
    return in_warns_list
