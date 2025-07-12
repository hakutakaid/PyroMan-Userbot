import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_filters_table():
    """Membuat tabel 'filters' jika belum ada."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'filters'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS filters (
                    chat_id TEXT NOT NULL,
                    keyword TEXT NOT NULL,
                    reply TEXT,
                    f_mesg_id INTEGER, -- Numeric di SQLAlchemy menjadi INTEGER di SQLite
                    PRIMARY KEY (chat_id, keyword)
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'filters' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'filters': {e}")
            return False
    return False

# Panggil fungsi untuk membuat tabel filters saat file ini dimuat
if DB_AVAILABLE:
    create_filters_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat filters_sql.py.")

---

## Fungsi Manajemen Filter

def get_filter(chat_id: int | str, keyword: str) -> dict | None:
    """
    Mendapatkan filter berdasarkan chat_id dan keyword.
    Mengembalikan dict filter atau None jika tidak ditemukan.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mendapatkan filter.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT chat_id, keyword, reply, f_mesg_id FROM filters WHERE chat_id = ? AND keyword = ?",
                           (str(chat_id), keyword))
            row = cursor.fetchone()
            if row:
                LOGGER(__name__).info(f"Filter ditemukan untuk chat {chat_id}, keyword '{keyword}'.")
                # Mengubah row menjadi dictionary agar kompatibel dengan objek Filters sebelumnya
                return {
                    "chat_id": row[0],
                    "keyword": row[1],
                    "reply": row[2],
                    "f_mesg_id": row[3]
                }
            else:
                LOGGER(__name__).info(f"Filter tidak ditemukan untuk chat {chat_id}, keyword '{keyword}'.")
                return None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mendapatkan filter: {e}")
            return None
    return None


def get_filters(chat_id: int | str) -> list[dict]:
    """
    Mendapatkan semua filter untuk chat_id tertentu.
    Mengembalikan list berisi dict filter.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mendapatkan filter.")
        return []

    conn, cursor = get_db_connection()
    filters_list = []
    if conn and cursor:
        try:
            cursor.execute("SELECT chat_id, keyword, reply, f_mesg_id FROM filters WHERE chat_id = ?", (str(chat_id),))
            rows = cursor.fetchall()
            for row in rows:
                filters_list.append({
                    "chat_id": row[0],
                    "keyword": row[1],
                    "reply": row[2],
                    "f_mesg_id": row[3]
                })
            LOGGER(__name__).info(f"{len(filters_list)} filter ditemukan untuk chat {chat_id}.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mendapatkan semua filter: {e}")
    return filters_list


def add_filter(chat_id: int | str, keyword: str, reply: str, f_mesg_id: int) -> bool:
    """
    Menambahkan filter baru atau memperbarui filter yang sudah ada.
    Mengembalikan True jika filter baru ditambahkan, False jika diperbarui.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menambahkan filter.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            to_check = get_filter(chat_id, keyword) # Menggunakan fungsi get_filter yang sudah dimigrasi
            
            if not to_check:
                # Filter tidak ada, sisipkan yang baru
                cursor.execute("INSERT INTO filters (chat_id, keyword, reply, f_mesg_id) VALUES (?, ?, ?, ?)",
                               (str(chat_id), keyword, reply, f_mesg_id))
                conn.commit()
                LOGGER(__name__).info(f"Filter baru ditambahkan: chat_id={chat_id}, keyword='{keyword}'.")
                return True
            else:
                # Filter sudah ada, perbarui
                cursor.execute("UPDATE filters SET reply = ?, f_mesg_id = ? WHERE chat_id = ? AND keyword = ?",
                               (reply, f_mesg_id, str(chat_id), keyword))
                conn.commit()
                LOGGER(__name__).info(f"Filter diperbarui: chat_id={chat_id}, keyword='{keyword}'.")
                return False # Mengembalikan False karena filter diperbarui, bukan baru ditambahkan
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menambahkan/memperbarui filter: {e}")
            return False
    return False


def remove_filter(chat_id: int | str, keyword: str) -> bool:
    """
    Menghapus filter berdasarkan chat_id dan keyword.
    Mengembalikan True jika filter berhasil dihapus, False jika tidak ditemukan.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menghapus filter.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            to_check = get_filter(chat_id, keyword) # Menggunakan fungsi get_filter yang sudah dimigrasi
            if not to_check:
                LOGGER(__name__).info(f"Filter tidak ditemukan untuk dihapus: chat_id={chat_id}, keyword='{keyword}'.")
                return False
            else:
                cursor.execute("DELETE FROM filters WHERE chat_id = ? AND keyword = ?",
                               (str(chat_id), keyword))
                conn.commit()
                LOGGER(__name__).info(f"Filter berhasil dihapus: chat_id={chat_id}, keyword='{keyword}'.")
                return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menghapus filter: {e}")
            return False
    return False

