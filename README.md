PyroMan-Userbot Telegram
PyroMan-Userbot adalah userbot Telegram modular yang berjalan di Python 3 dengan Library Pyrogram.
Saya membuat repository ini untuk bersenang-senang sekaligus membantu Anda mengelola grup secara efisien dan untuk mengurangi kebosanan saat menggunakan Telegram.
⚠️ Disclaimer
Saya tidak bertanggung jawab atas penyalahgunaan bot ini.
Gunakan bot ini dengan risiko Anda sendiri.
Gunakan userbot ini dengan bijak.
Ketika Anda sudah memasang userbot ini, berarti Anda sudah siap dengan risikonya.

⚙️ Cara Memasang di VPS (Virtual Private Server)
Berikut adalah langkah-langkah untuk menginstal PyroMan-Userbot di VPS Anda:
 * Akses VPS Anda
   Gunakan SSH untuk terhubung ke VPS Anda. Contoh:
   ssh user@your_vps_ip

 * Perbarui Sistem
   Pastikan sistem Anda up-to-date:
   sudo apt update && sudo apt upgrade -y

 * Kloning Repository
   Kloning repository PyroMan-Userbot ke VPS Anda:
   git clone https://github.com/mrismanaziz/PyroMan-Userbot.git
cd PyroMan-Userbot

 * Buat Virtual Environment dan Instal Dependensi
   Sangat disarankan untuk menggunakan virtual environment untuk mengelola dependensi.
   python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

 * Konfigurasi (Environment Variables)
   Anda perlu mengatur environment variables seperti API_ID, API_HASH, dan STRING_SESSION. Cara termudah adalah membuat file .env di root directory PyroMan-Userbot dan menambahkannya di sana:
   API_ID=YOUR_API_ID
API_HASH=YOUR_API_HASH
STRING_SESSION=YOUR_PYROGRAM_STRING_SESSION

   (Ganti YOUR_API_ID, YOUR_API_HASH, dan YOUR_PYROGRAM_STRING_SESSION dengan nilai Anda.)
 * Jalankan Bot
   Setelah semua dependensi terinstal dan konfigurasi selesai, Anda bisa menjalankan bot:
   python3 -m pyroman

   Untuk menjalankan bot di latar belakang secara terus-menerus, Anda bisa menggunakan screen atau tmux.
🖇 Meng-Generate Pyrogram String Session
> Anda memerlukan APP ID & API HASH Telegram untuk mengambil sesi Pyrogram. Ambil APP ID dan API Hash di my.telegram.org.
> 
 * Generate Session via Repl.it
 * Generate Session via Telegram String Generation Bot
🏷 Dukungan
 * Follow Channel @Lunatic0de untuk info Update bot.
 * Gabung Group @SharingUserbot untuk diskusi, pelaporan bug, dan bantuan tentang PyroMan-Userbot.
👨🏻‍💻 Kredit
 * Dan untuk Pyrogram
 * Risman untuk PyroMan-Userbot
Terima Kasih Khusus untuk Semua yang Telah Membantu Membuat Userbot ini Luar Biasa!
 * TeamDerUntergang : SedenUserBot
 * TheHamkerCat : WilliamButcherBot
 * TeamYukki : YukkiMusicBot
 * ITZ-ZAID : Zaid-UserBot
 * Risman : PyroMan-Userbot
 * Tofikdn : Tede
 * Toni : Prime-UserBot
📑 Lisensi
Berlisensi di bawah GNU General Public License v3.0. Semua desain dibuat oleh @mrismanaziz.
