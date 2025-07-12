import os
import sqlite3

class Logger:
    def warning(self, msg):
        print(f"WARNING: {msg}")
    def info(self, msg):
        print(f"INFO: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")

LOGGER = lambda name: Logger()

DB_URL = "sqlite:////storage/emulated/0/PyroMan-Userbot/projectman.db"

SPAMBOT = "SPAMBOT"

SQLITE_DB_PATH = DB_URL.replace("sqlite:///", "")

db_dir = os.path.dirname(SQLITE_DB_PATH)
if db_dir and not os.path.exists(db_dir):
    try:
        os.makedirs(db_dir)
        LOGGER(__name__).info(f"Direktori database dibuat: {db_dir}")
    except OSError as e:
        LOGGER(__name__).error(f"Gagal membuat direktori database {db_dir}: {e}")

CONN = None
CURSOR = None
DB_AVAILABLE = False
BOTINLINE_AVAILABLE = False

def get_db_connection():
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
            CONN = None
            CURSOR = None
    return CONN, CURSOR

def close_db_connection():
    global CONN, CURSOR, DB_AVAILABLE
    if CONN:
        CONN.close()
        CONN = None
        CURSOR = None
        DB_AVAILABLE = False
        LOGGER(__name__).info("Koneksi database ditutup.")

def create_tables():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel.")
        return False

    try:
        conn, cursor = get_db_connection()
        if conn and cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS no_log_chats (
                    chat_id INTEGER PRIMARY KEY UNIQUE NOT NULL
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'no_log_chats' berhasil dibuat atau sudah ada.")
            return True
        else:
            return False
    except sqlite3.Error as e:
        LOGGER(__name__).error(f"Gagal membuat tabel 'no_log_chats': {e}")
        return False

def start_db():
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

def is_approved(chat_id: int) -> bool:
    if not DB_AVAILABLE:
        return False
    
    conn, cursor = get_db_connection()
    if conn and cursor:
        cursor.execute("SELECT 1 FROM no_log_chats WHERE chat_id = ?", (chat_id,))
        result = cursor.fetchone()
        return result is not None
    return False

def approve(chat_id: int):
    if not DB_AVAILABLE:
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT INTO no_log_chats (chat_id) VALUES (?)", (chat_id,))
            conn.commit()
        except sqlite3.IntegrityError:
            pass # chat_id sudah ada, tidak perlu dilakukan apa-apa
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menyetujui chat {chat_id}: {e}")

def disapprove(chat_id: int):
    if not DB_AVAILABLE:
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM no_log_chats WHERE chat_id = ?", (chat_id,))
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membatalkan persetujuan chat {chat_id}: {e}")

