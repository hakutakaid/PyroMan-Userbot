import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, close_db_connection, DB_AVAILABLE, LOGGER

Owner = 0

MY_AFK = {}

def create_afk_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel afk.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS afk (
                    user_id TEXT PRIMARY KEY,
                    is_afk INTEGER NOT NULL,
                    reason TEXT
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'afk' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel afk: {e}")
            return False
    return False

if DB_AVAILABLE:
    create_afk_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat afk_db.py.")

def set_afk(afk: bool, reason: str):
    global MY_AFK
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengatur status AFK.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM afk WHERE user_id = ?", (str(Owner),))
            cursor.execute("INSERT INTO afk (user_id, is_afk, reason) VALUES (?, ?, ?)",
                           (str(Owner), 1 if afk else 0, reason))
            conn.commit()
            MY_AFK[Owner] = {"afk": afk, "reason": reason}
            LOGGER(__name__).info(f"Status AFK untuk Owner {Owner} diatur: afk={afk}, reason='{reason}'")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mengatur status AFK: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba mengatur AFK.")

def get_afk() -> dict | None:
    return MY_AFK.get(Owner)

def __load_afk():
    global MY_AFK
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat memuat status AFK.")
        return

    MY_AFK = {}
    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT user_id, is_afk, reason FROM afk")
            rows = cursor.fetchall()
            for row in rows:
                user_id, is_afk_int, reason = row
                MY_AFK[int(user_id)] = {"afk": bool(is_afk_int), "reason": reason}
            LOGGER(__name__).info("Status AFK berhasil dimuat dari database.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal memuat status AFK dari database: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba memuat AFK.")

__load_afk()
