import os
import sqlite3

# Asumsi ProjectMan dan LOGGER sudah didefinisikan.
# Contoh placeholder jika Anda tidak punya ProjectMan dan LOGGER:
class Logger:
    def warning(self, msg):
        print(f"WARNING: {msg}")
    def info(self, msg):
        print(f"INFO: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")

LOGGER = lambda name: Logger()

# Asumsi DB_URL sudah didefinisikan di ProjectMan
# Contoh placeholder untuk DB_URL:
# Untuk kasus di Android (jalur yang Anda berikan):
# Pastikan direktori ProjectMan-Userbot ada dan dapat ditulis.
# Misalnya, "/data/data/com.termux/files/home/pyroman_db.db" atau di /sdcard
DB_URL = "sqlite:////storage/emulated/0/PyroMan-Userbot/projectman.db"


SPAMBOT = "SPAMBOT"

# Ekstrak jalur file database dari DB_URL
SQLITE_DB_PATH = DB_URL.replace("sqlite:///", "")

# Pastikan direktori untuk database ada
db_dir = os.path.dirname(SQLITE_DB_PATH)
if db_dir and not os.path.exists(db_dir):
    try:
        os.makedirs(db_dir)
        LOGGER(__name__).info(f"Direktori database dibuat: {db_dir}")
    except OSError as e:
        LOGGER(__name__).error(f"Gagal membuat direktori database {db_dir}: {e}")
        # Jika direktori tidak bisa dibuat, atur DB_AVAILABLE ke False di awal
        # dan mungkin ubah SQLITE_DB_PATH ke lokasi yang bisa ditulis
        # atau hentikan eksekusi jika database sangat krusial.

# Variabel global untuk koneksi database
CONN = None
CURSOR = None
DB_AVAILABLE = False
BOTINLINE_AVAILABLE = False # Perbaikan typo

def get_db_connection():
    """Mendapatkan koneksi database global. Membuat koneksi jika belum ada."""
    global CONN, CURSOR, DB_AVAILABLE
    if CONN is None:
        try:
            CONN = sqlite3.connect(SQLITE_DB_PATH)
            CURSOR = CONN.cursor()
            DB_AVAILABLE = True
            LOGGER(__name__).info(f"Berhasil terhubung ke database SQLite: {SQLITE_DB_PATH}")
        except sqlite3.OperationalError as e:
            LOGGER(__name__).error(f"Gagal terhubung ke database SQLite di {SQLITE_DB_PATH}: {e}")
            DB_AVAILABLE = False
            CONN = None # Pastikan CONN diatur ke None jika koneksi gagal
            CURSOR = None
    return CONN, CURSOR

def close_db_connection():
    """Menutup koneksi database."""
    global CONN, CURSOR, DB_AVAILABLE
    if CONN:
        CONN.close()
        CONN = None
        CURSOR = None
        DB_AVAILABLE = False
        LOGGER(__name__).info("Koneksi database ditutup.")

def create_tables():
    """Membuat tabel-tabel yang diperlukan."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel.")
        return False

    try:
        conn, cursor = get_db_connection()
        if conn and cursor:
            # --- DEFINISIKAN SKEMA TABEL ANDA DI SINI ---
            # Contoh tabel:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spam_settings (
                    id INTEGER PRIMARY KEY,
                    chat_id INTEGER UNIQUE NOT NULL,
                    enabled BOOLEAN NOT NULL DEFAULT 0
                );
            ''')
            # Tambahkan tabel lain sesuai kebutuhan ProjectMan Anda, misalnya:
            # cursor.execute('''
            #     CREATE TABLE IF NOT EXISTS users (
            #         user_id INTEGER PRIMARY KEY,
            #         username TEXT
            #     );
            # ''')
            conn.commit()
            LOGGER(__name__).info("Tabel berhasil dibuat atau sudah ada.")
            return True
        else:
            return False
    except sqlite3.Error as e:
        LOGGER(__name__).error(f"Gagal membuat tabel: {e}")
        return False

def start_db():
    """Fungsi awal untuk menginisialisasi koneksi database."""
    global DB_AVAILABLE
    conn, cursor = get_db_connection()
    if conn and cursor:
        if create_tables():
            DB_AVAILABLE = True
            LOGGER(__name__).info("Database sudah siap.")
            return True
        else:
            DB_AVAILABLE = False
            return False
    else:
        DB_AVAILABLE = False
        LOGGER(__name__).error("Gagal memulai koneksi database.")
        return False

# Panggil fungsi inisialisasi database saat skrip dimuat
# Ini akan menggantikan logika try-except start() dan mulaisql() yang lama
try:
    if start_db():
        DB_AVAILABLE = True
    else:
        DB_AVAILABLE = False
except Exception as e:
    LOGGER(__name__).error(f"Kesalahan saat memulai database: {e}")
    DB_AVAILABLE = False

if not DB_AVAILABLE:
    LOGGER(__name__).warning(
        "Database tidak tersedia. Fitur yang bergantung pada database mungkin mengalami masalah."
    )

