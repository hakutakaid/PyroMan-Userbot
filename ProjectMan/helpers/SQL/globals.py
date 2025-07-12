import sqlite3

# Asumsikan ProjectMan.helpers.SQL sudah diinisialisasi dan menyediakan koneksi DB
# dan LOGGER.
from ProjectMan.helpers.SQL.__init__ import get_db_connection, DB_AVAILABLE, LOGGER

def create_globals_table():
    """Membuat tabel 'globals' jika belum ada."""
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat membuat tabel 'globals'.")
        return False

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            # Menggunakan dua kolom sebagai PRIMARY KEY (composite primary key)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS globals (
                    variable TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (variable, value)
                );
            ''')
            conn.commit()
            LOGGER(__name__).info("Tabel 'globals' berhasil dibuat atau sudah ada.")
            return True
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal membuat tabel 'globals': {e}")
            return False
    return False

# Panggil fungsi untuk membuat tabel globals saat file ini dimuat
if DB_AVAILABLE:
    create_globals_table()
else:
    LOGGER(__name__).error("Database tidak tersedia saat memuat globals.py.")

---

## Fungsi Manajemen Variabel Global

def gvarstatus(variable: str) -> str | None:
    """
    Mendapatkan nilai dari variabel global.
    Mengembalikan nilai variabel (str) atau None jika tidak ditemukan atau ada error DB.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat mendapatkan status gvar.")
        return None

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("SELECT value FROM globals WHERE variable = ?", (str(variable),))
            row = cursor.fetchone()
            if row:
                return row[0]  # Mengambil nilai dari tuple hasil
            else:
                return None
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal mendapatkan gvar '{variable}': {e}")
            return None
    return None


def addgvar(variable: str, value: str):
    """
    Menambahkan atau memperbarui variabel global.
    Jika variabel sudah ada, nilai akan diperbarui.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menambahkan gvar.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            # SQLite tidak memiliki satu metode 'upsert' seperti PostgreSQL.
            # Kita bisa menggunakan REPLACE INTO atau mencoba INSERT dan jika gagal, UPDATE.
            # Karena primary key adalah (variable, value), REPLACE INTO akan mengganti
            # jika ada variabel DENGAN NILAI YANG SAMA.
            # Jika variabel BISA memiliki banyak nilai (seperti di SQLAlchemy dengan value
            # yang juga PK), kita harus berhati-hati.
            # Berdasarkan kode asli, sepertinya hanya ada satu nilai per variabel.
            # Logika asli: if exists, delete, then add.
            # Ini bisa disederhanakan dengan UPDATE atau REPLACE INTO.
            # Mari kita gunakan UPDATE lalu jika tidak ada, INSERT.

            cursor.execute("UPDATE globals SET value = ? WHERE variable = ?", (value, str(variable)))
            if cursor.rowcount == 0:
                # Jika tidak ada baris yang diperbarui, berarti variabel belum ada, maka sisipkan
                cursor.execute("INSERT INTO globals (variable, value) VALUES (?, ?)", (str(variable), value))
                LOGGER(__name__).info(f"Gvar baru ditambahkan: '{variable}' = '{value}'.")
            else:
                LOGGER(__name__).info(f"Gvar diperbarui: '{variable}' = '{value}'.")
            conn.commit()
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menambahkan/memperbarui gvar '{variable}': {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba menambahkan gvar.")


def delgvar(variable: str):
    """
    Menghapus variabel global.
    """
    if not DB_AVAILABLE:
        LOGGER(__name__).warning("Database tidak tersedia, tidak dapat menghapus gvar.")
        return

    conn, cursor = get_db_connection()
    if conn and cursor:
        try:
            cursor.execute("DELETE FROM globals WHERE variable = ?", (str(variable),))
            if cursor.rowcount > 0: # Memeriksa apakah ada baris yang terpengaruh (dihapus)
                conn.commit()
                LOGGER(__name__).info(f"Gvar '{variable}' berhasil dihapus.")
            else:
                LOGGER(__name__).info(f"Gvar '{variable}' tidak ditemukan untuk dihapus.")
        except sqlite3.Error as e:
            LOGGER(__name__).error(f"Gagal menghapus gvar '{variable}': {e}")
    else:
        LOGGER(__name__).error("Koneksi database tidak valid saat mencoba menghapus gvar.")

