import sqlite3

# Asumsikan ProjectMan.helpers.SQL sudah diinisialisasi dan menyediakan koneksi DB
# dan LOGGER.
from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

# Asumsi Anda akan mendapatkan ID Owner dari Pyrogram Client di luar modul ini,
# karena Client.get_me().id membutuhkan inisialisasi Pyrogram Client.
# Kita akan gunakan placeholder untuk Owner di sini, dan Anda harus memastikan
# nilai ini diatur dengan benar saat fungsi-fungsi ini dipanggil.
# Contoh: Owner = some_client_instance.get_me().id
Owner = None # Akan diatur saat runtime oleh kode yang memanggil backup_identity

def create_cloner_table():
    """Membuat tabel 'cloner' jika belum ada."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'cloner'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cloner (
                    user_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    bio TEXT
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'cloner' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'cloner': {e}")
            return False
    return False

# Panggil fungsi untuk membuat tabel cloner saat file ini dimuat
if DB_AVAILABLE:
    create_cloner_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat cloner_db.py.")

---

## Fungsi Manajemen Identitas

def backup_identity(owner_id: int, first_name: str, last_name: str, bio: str):
    """
    Mencadangkan identitas (nama depan, nama belakang, bio) pengguna bot.
    Owner ID harus diberikan secara eksplisit.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mencadangkan identitas.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            # Hapus entri yang ada (jika ada) untuk owner_id
            cursor.execute("DELETE FROM cloner WHERE user_id = ?", (str(owner_id),))

            # Sisipkan data identitas baru
            cursor.execute("INSERT INTO cloner (user_id, first_name, last_name, bio) VALUES (?, ?, ?, ?)",
                           (str(owner_id), first_name, last_name, bio))
            conn.commit()
            LOGGER(__name__).info(f"Identitas untuk user {owner_id} berhasil dicadangkan.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mencadangkan identitas: {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba mencadangkan identitas.")


def restore_identity(owner_id: int) -> tuple | None:
    """
    Mengembalikan identitas (nama depan, nama belakang, bio) pengguna bot.
    Mengembalikan tuple (first_name, last_name, bio) atau None jika tidak ditemukan.
    Owner ID harus diberikan secara eksplisit.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mengembalikan identitas.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT first_name, last_name, bio FROM cloner WHERE user_id = ?", (str(owner_id),))
            row = cursor.fetchone()
            if row:
                LOGGER(__name__).info(f"Identitas untuk user {owner_id} berhasil dikembalikan.")
                return row # row adalah tuple (first_name, last_name, bio)
            else:
                LOGGER(__name__).info(f"Tidak ada identitas yang dicadangkan untuk user {owner_id}.")
                return None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mengembalikan identitas: {e}")
            return None
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba mengembalikan identitas.")
        return None

