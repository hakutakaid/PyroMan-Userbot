import sqlite3

# Asumsikan ProjectMan.helpers.SQL sudah diinisialisasi dan menyediakan koneksi DB
# Misalnya, dari file __init__.py yang sudah dimigrasi sebelumnya.
# Anda perlu memastikan bahwa `get_db_connection` dan `close_db_connection`
# sudah tersedia dari import tersebut atau dari lokasi lain yang sesuai.

# Contoh impor jika afk_db.py berada di direktori yang sama dengan __init__.py yang sudah dimodifikasi:
from ProjectMan.helpers.SQL.__init__ import get_db_connection, close_db_connection, DB_AVAILABLE, LOGGER

# Jika Anda mengimpor dari direktori yang sama, sesuaikan jalur impornya
# import sys
# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Menyesuaikan path untuk import ProjectMan
# from ProjectMan.helpers.SQL.__init__ import get_db_connection, close_db_connection, DB_AVAILABLE, LOGGER


Owner = 0  # Diasumsikan Owner adalah ID pengguna yang dikelola oleh bot

MY_AFK = {}

def create_afk_table():
    """Membuat tabel afk jika belum ada."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel afk.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS afk (
                    user_id TEXT PRIMARY KEY,
                    is_afk INTEGER NOT NULL, -- SQLite menggunakan INTEGER untuk BOOLEAN (0 atau 1)
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

# Panggil fungsi untuk membuat tabel afk saat file ini dimuat
if DB_AVAILABLE:
    create_afk_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat afk_db.py.")


def set_afk(afk: bool, reason: str):
    """Mengatur status AFK untuk Owner."""
    global MY_AFK
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengatur status AFK.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            # Hapus entri yang ada (jika ada) untuk Owner
            cursor.execute("DELETE FROM afk WHERE user_id = ?", (str(Owner),))

            # Sisipkan data AFK yang baru
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
    """Mendapatkan status AFK untuk Owner dari memori."""
    return MY_AFK.get(Owner)


def __load_afk():
    """Memuat semua status AFK dari database ke memori."""
    global MY_AFK
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat memuat status AFK.")
        return

    MY_AFK = {} # Bersihkan cache sebelumnya
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


# Panggil __load_afk() untuk memuat data saat modul diimpor
__load_afk()
