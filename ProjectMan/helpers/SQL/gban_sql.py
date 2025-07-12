import sqlite3

# Asumsikan ProjectMan.helpers.SQL sudah diinisialisasi dan menyediakan koneksi DB
# dan LOGGER.
from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_gban_table():
    """Membuat tabel 'gban' jika belum ada."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'gban'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS gban (
                    sender TEXT PRIMARY KEY
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'gban' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'gban': {e}")
            return False
    return False

# Panggil fungsi untuk membuat tabel gban saat file ini dimuat
if DB_AVAILABLE:
    create_gban_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat gban.py.")

---

## Fungsi Manajemen GBan

def is_gbanned(sender: int | str) -> bool | None:
    """
    Memeriksa apakah pengirim (sender) di-gban.
    Mengembalikan True jika di-gban, False jika tidak, atau None jika ada error DB.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat memeriksa status gban.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT 1 FROM gban WHERE sender = ?", (str(sender),))
            row = cursor.fetchone()
            return row is not None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal memeriksa status gban untuk {sender}: {e}")
            return None
    return None


def gbanned_users() -> list[str] | None:
    """
    Mendapatkan daftar semua ID pengirim yang di-gban.
    Mengembalikan list ID pengirim atau None jika ada error DB.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengambil daftar gban.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT sender FROM gban")
            rows = cursor.fetchall()
            return [row[0] for row in rows] # Mengambil elemen pertama dari setiap tuple (sender ID)
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mengambil daftar gban: {e}")
            return None
    return None


def gban(sender: int | str):
    """
    Menambahkan pengirim (sender) ke daftar gban.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat melakukan gban.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            # Menggunakan INSERT OR IGNORE untuk mencegah error jika sender sudah ada
            cursor.execute("INSERT OR IGNORE INTO gban (sender) VALUES (?)", (str(sender),))
            conn.commit()
            LOGGER(__name__).info(f"Pengirim {sender} berhasil di-gban (jika belum ada).")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal melakukan gban untuk {sender}: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba gban.")


def ungban(sender: int | str):
    """
    Menghapus pengirim (sender) dari daftar gban.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat melakukan ungban.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM gban WHERE sender = ?", (str(sender),))
            if cursor.rowcount > 0: # Memeriksa apakah ada baris yang terpengaruh (dihapus)
                conn.commit()
                LOGGER(__name__).info(f"Pengirim {sender} berhasil di-ungban.")
            else:
                LOGGER(__name__).info(f"Pengirim {sender} tidak ditemukan di daftar gban.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal melakukan ungban untuk {sender}: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba ungban.")

