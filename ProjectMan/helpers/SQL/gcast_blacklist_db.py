# ProjectMan/helpers/SQL/gcast_blacklist_db.py

import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

DEFAULT_BLACKLIST_CHAT_IDS = [-1001473548283]

def create_gcast_blacklist_table():
    """Membuat tabel 'gcast_blacklist' jika belum ada dan menambahkan ID default."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'gcast_blacklist'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gcast_blacklist (
                    chat_id INTEGER PRIMARY KEY NOT NULL
                );
            ''')
            for chat_id in DEFAULT_BLACKLIST_CHAT_IDS:
                cursor.execute("INSERT OR IGNORE INTO gcast_blacklist (chat_id) VALUES (?)", (chat_id,))
                if cursor.rowcount > 0:
                    LOGGER(__name__).info(f"Chat ID default {chat_id} berhasil ditambahkan ke blacklist.")
                else:
                    LOGGER(__name__).info(f"Chat ID default {chat_id} sudah ada di blacklist.")
            
            conn.commit()
            LOGGER(__name__).info("Tabel 'gcast_blacklist' berhasil dibuat atau sudah ada dan ID default diproses.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'gcast_blacklist' atau menambahkan ID default: {e}")
            return False
    return False

def add_chat_to_blacklist(chat_id: int) -> bool:
    """Menambahkan ID chat ke blacklist GCAST."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menambahkan chat ke blacklist.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR IGNORE INTO gcast_blacklist (chat_id) VALUES (?)", (chat_id,))
            conn.commit()
            if cursor.rowcount > 0:
                LOGGER(__name__).info(f"Chat {chat_id} ditambahkan ke GCAST blacklist.")
                return True
            else:
                LOGGER(__name__).info(f"Chat {chat_id} sudah ada di GCAST blacklist.")
                return False
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menambahkan chat {chat_id} ke GCAST blacklist: {e}")
            return False
    return False

def remove_chat_from_blacklist(chat_id: int) -> bool:
    """Menghapus ID chat dari blacklist GCAST."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menghapus chat dari blacklist.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM gcast_blacklist WHERE chat_id = ?", (chat_id,))
            conn.commit()
            if cursor.rowcount > 0:
                LOGGER(__name__).info(f"Chat {chat_id} dihapus dari GCAST blacklist.")
                return True
            else:
                LOGGER(__name__).info(f"Chat {chat_id} tidak ditemukan di GCAST blacklist.")
                return False
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menghapus chat {chat_id} dari GCAST blacklist: {e}")
            return False
    return False

def get_gcast_blacklist() -> list[int]:
    """Mengambil semua ID chat dari blacklist GCAST."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengambil GCAST blacklist.")
        return []

    conn, cursor = get_db_connection()
    blacklist = []
    if conn and cursor:
        try:
            cursor.execute("SELECT chat_id FROM gcast_blacklist")
            rows = cursor.fetchall()
            blacklist = [row[0] for row in rows]
            LOGGER(__name__).info(f"Mengambil {len(blacklist)} chat dari GCAST blacklist.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mengambil GCAST blacklist: {e}")
    return blacklist

if DB_AVAILABLE:
    create_gcast_blacklist_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat gcast_blacklist_db.py.")