# PyroMan-Userbot Telegram

PyroMan-Userbot adalah userbot Telegram modular yang berjalan di **Python 3** dengan **Library Pyrogram**.

Saya membuat *repository* ini untuk bersenang-senang sekaligus membantu Anda mengelola grup secara efisien dan untuk mengurangi kebosanan saat menggunakan Telegram.

---

## ⚠️ Disclaimer


Saya tidak bertanggung jawab atas penyalahgunaan bot ini.
Gunakan bot ini dengan risiko Anda sendiri.
Gunakan userbot ini dengan bijak.
Ketika Anda sudah memasang userbot ini, berarti Anda sudah siap dengan risikonya.

---

## ⚙️ Cara Memasang di VPS (Virtual Private Server)

Berikut adalah langkah-langkah untuk menginstal PyroMan-Userbot di VPS Anda:

1.  **Akses VPS Anda**
    Gunakan SSH untuk terhubung ke VPS Anda. Contoh:
    ```bash
    ssh user@your_vps_ip
    ```

2.  **Perbarui Sistem**
    Pastikan sistem Anda *up-to-date*:
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

3.  **Kloning *Repository***
    *Kloning* *repository* PyroMan-Userbot ke VPS Anda:
    ```bash
    git clone [https://github.com/hakutakaid/PyroMan-Userbot.git](https://github.com/hakutakaid/PyroMan-Userbot.git)
    cd PyroMan-Userbot
    ```

4.  **Buat *Virtual Environment* dan Instal Dependensi**
    Sangat disarankan untuk menggunakan *virtual environment* untuk mengelola dependensi.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    ```

5.  **Konfigurasi (*Environment Variables*)**
    Anda perlu mengatur *environment variables* seperti `API_ID`, `API_HASH`, dan `STRING_SESSION`. Cara termudah adalah membuat file `.env` di *root directory* PyroMan-Userbot dan menambahkannya di sana:
    ```
    API_ID=YOUR_API_ID
    API_HASH=YOUR_API_HASH
    STRING_SESSION=YOUR_PYROGRAM_STRING_SESSION
    ```
    *(Ganti `YOUR_API_ID`, `YOUR_API_HASH`, dan `YOUR_PYROGRAM_STRING_SESSION` dengan nilai Anda.)*

6.  **Jalankan Bot**
    Setelah semua dependensi terinstal dan konfigurasi selesai, Anda bisa menjalankan bot:
    ```bash
    python3 -m pyroman
    ```
    Untuk menjalankan bot di latar belakang secara terus-menerus, Anda bisa menggunakan `screen` atau `tmux`.

---

## 🖇 Meng-*Generate* Pyrogram String Session

> Anda memerlukan **APP ID** & **API HASH** Telegram untuk mengambil sesi Pyrogram. Ambil **APP ID** dan **API Hash** di [my.telegram.org](https://my.telegram.org).

-   *Generate Session* via [Repl.it](https://repl.it/@mrismanaziz/stringen?lite=1&outputonly=1)
-   *Generate Session* via [Telegram String Generation Bot](https://t.me/StringManRobot)

---

## 🏷 Dukungan

-   *Follow Channel* [@Lunatic0de](https://t.me/Lunatic0de) untuk info *Update* bot.
-   Gabung *Group* [@SharingUserbot](https://t.me/SharingUserbot) untuk diskusi, pelaporan *bug*, dan bantuan tentang PyroMan-Userbot.

---

## 👨🏻‍💻 Kredit

-   [Dan](https://github.com/delivrance) untuk [Pyrogram](https://github.com/pyrogram/pyrogram)
-   [Risman](https://github.com/mrismanaziz) untuk [PyroMan-Userbot](https://github.com/mrismanaziz/PyroMan-Userbot)

#### Terima Kasih Khusus untuk [Semua](https://github.com/mrismanaziz/PyroMan-Userbot/graphs/contributors) yang Telah Membantu Membuat *Userbot* ini Luar Biasa!

-   [TeamDerUntergang](https://github.com/TeamDerUntergang/Telegram-SedenUserBot) : SedenUserBot
-   [TheHamkerCat](https://github.com/TheHamkerCat/WilliamButcherBot) : WilliamButcherBot
-   [TeamYukki](https://github.com/TeamYukki/YukkiMusicBot) : YukkiMusicBot
-   [ITZ-ZAID](https://github.com/ITZ-ZAID) : Zaid-UserBot
-   [Risman](https://github.com/mrismanaziz) : PyroMan-Userbot
-   [Tofikdn](https://github.com/tofikdn) : Tede
-   [Toni](https://github.com/Toni880) : Prime-UserBot

---

## 📑 Lisensi

Berlisensi di bawah [GNU General Public License v3.0](https://github.com/mrismanaziz/PyroMan-Userbot/blob/Man-Userbot/LICENSE). Semua desain dibuat oleh [@mrismanaziz](https://github.com/mrismanaziz).