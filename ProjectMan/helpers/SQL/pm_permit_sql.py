import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_pmpermit_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'pmpermit'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pmpermit (
                    chat_id TEXT PRIMARY KEY
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'pmpermit' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'pmpermit': {e}")
            return False
    return False

if DB_AVAILABLE:
    create_pmpermit_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat pmpermit.py.")



## Fungsi Manajemen Izin PM

def is_approved(chat_id: int | str) -> bool | None:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat memeriksa status izin PM.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT 1 FROM pmpermit WHERE chat_id = ?", (str(chat_id),))
            row = cursor.fetchone()
            return row is not None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal memeriksa status izin PM untuk chat {chat_id}: {e}")
            return None
    return None

def approve(chat_id: int | str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengizinkan PM.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR IGNORE INTO pmpermit (chat_id) VALUES (?)", (str(chat_id),))
            conn.commit()
            LOGGER(__name__).info(f"Chat {chat_id} telah diizinkan untuk PM (jika belum).")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mengizinkan PM untuk chat {chat_id}: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba mengizinkan PM.")

def dissprove(chat_id: int | str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat tidak mengizinkan PM.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM pmpermit WHERE chat_id = ?", (str(chat_id),))
            if cursor.rowcount > 0:
                conn.commit()
                LOGGER(__name__).info(f"Chat {chat_id} telah tidak diizinkan untuk PM.")
            else:
                LOGGER(__name__).info(f"Chat {chat_id} tidak ditemukan dalam daftar izin PM.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal tidak mengizinkan PM untuk chat {chat_id}: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba tidak mengizinkan PM.")
