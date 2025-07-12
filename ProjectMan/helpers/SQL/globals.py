import sqlite3

from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_globals_table():
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'globals'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS globals (
                    variable TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (variable)
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'globals' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'globals': {e}")
            return False
    return False

if DB_AVAILABLE:
    create_globals_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat globals.py.")

---

## Fungsi Manajemen Variabel Global

def gvarstatus(variable: str) -> str | None:
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mendapatkan status gvar.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT value FROM globals WHERE variable = ?", (variable,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mendapatkan gvar '{variable}': {e}")
            return None
    return None


def addgvar(variable: str, value: str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menambahkan gvar.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("INSERT OR REPLACE INTO globals (variable, value) VALUES (?, ?)", (variable, value))
            conn.commit()
            LOGGER(__name__).info(f"Gvar '{variable}' diatur ke '{value}'.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menambahkan/memperbarui gvar '{variable}': {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba menambahkan gvar.")


def delgvar(variable: str):
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menghapus gvar.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM globals WHERE variable = ?", (variable,))
            if cursor.rowcount > 0:
                conn.commit()
                LOGGER(__name__).info(f"Gvar '{variable}' berhasil dihapus.")
            else:
                LOGGER(__name__).info(f"Gvar '{variable}' tidak ditemukan untuk dihapus.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menghapus gvar '{variable}': {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba menghapus gvar.")
