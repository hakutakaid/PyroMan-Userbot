# Credits: @mrismanaziz
# Copyright (C) 2022 Pyro-ManUserbot
#
# This file is a part of < https://github.com/mrismanaziz/PyroMan-Userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/mrismanaziz/PyroMan-Userbot/blob/main/LICENSE/>.
#
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from config import CMD_HANDLER as cmd, BOTLOG_CHATID # Pastikan BOTLOG_CHATID diimpor dari config
from ProjectMan.helpers.basic import edit_or_reply
# Mengimpor langsung fungsi dari modul no_log_pms_sql yang sudah dimigrasi
from ProjectMan.helpers.SQL.no_log_pms_sql import is_approved, approve, disapprove
# Mengimpor langsung fungsi dari modul globals yang sudah dimigrasi
from ProjectMan.helpers.SQL.globals import addgvar, gvarstatus
from ProjectMan.helpers.tools import get_arg

from .help import add_command_help


class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


@Client.on_message(
    filters.private & filters.incoming & ~filters.service & ~filters.me & ~filters.bot
)
async def monito_p_m_s(client: Client, message: Message):
    # Logika tetap sama, hanya memanggil fungsi yang sudah dimigrasi
    if BOTLOG_CHATID == -100:
        return
    
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmlog_status = gvarstatus("PMLOG")
    if pmlog_status == "false":
        return

    # Periksa apakah chat_id disetujui untuk tidak di-log
    # Fungsi is_approved dari no_log_pms_sql sekarang mengembalikan bool atau None
    if not is_approved(message.chat.id) and message.chat.id != 777000:
        if LOG_CHATS_.RECENT_USER != message.chat.id:
            LOG_CHATS_.RECENT_USER = message.chat.id
            if LOG_CHATS_.NEWPM:
                # Perbarui pesan sebelumnya jika ada
                await LOG_CHATS_.NEWPM.edit(
                    LOG_CHATS_.NEWPM.text.replace(
                        "**💌 #NEW_MESSAGE**", # Asumsi ini bagian awal pesan Anda
                        f" • `{LOG_CHATS_.COUNT}` **Pesan**",
                    )
                )
                LOG_CHATS_.COUNT = 0 # Reset counter
            LOG_CHATS_.NEWPM = await client.send_message(
                BOTLOG_CHATID,
                f"💌 <b>#MENERUSKAN #PESAN_BARU</b>\n<b> • Dari :</b> {message.from_user.mention}\n<b> • User ID :</b> <code>{message.from_user.id}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        try:
            # Cari satu pesan terakhir dari chat_id dan forward
            async for pmlog in client.search_messages(message.chat.id, limit=1):
                await pmlog.forward(BOTLOG_CHATID)
            LOG_CHATS_.COUNT += 1
        except Exception as e: # Tangani exception spesifik daripada BaseException
            # Log error jika forwarding gagal
            LOGGER(__name__).error(f"Failed to forward PM log: {e}")
            pass # Lanjutkan eksekusi meskipun forwarding gagal


@Client.on_message(filters.group & filters.mentioned & filters.incoming)
async def log_tagged_messages(client: Client, message: Message):
    if BOTLOG_CHATID == -100:
        return

    # gvarstatus akan mengembalikan string "true" / "false" atau None
    gruplog_status = gvarstatus("GRUPLOG")
    if gruplog_status == "false":
        return

    # Periksa apakah chat_id disetujui untuk tidak di-log
    # Fungsi is_approved dari no_log_pms_sql sekarang mengembalikan bool atau None
    if is_approved(message.chat.id) or (BOTLOG_CHATID == -100):
        return
        
    result = f"<b>📨 #TAGS #MESSAGE</b>\n<b> • Dari : </b>{message.from_user.mention}"
    result += f"\n<b> • Grup : </b>{message.chat.title}"
    result += f"\n<b> • 👀 </b><a href = '{message.link}'>Lihat Pesan</a>"
    # Gunakan message.text jika ada, jika tidak, message.caption
    message_content = message.text if message.text else message.caption 
    if message_content: # Hanya tambahkan jika ada konten teks
        result += f"\n<b> • Message : </b><code>{message_content}</code>"
    
    await asyncio.sleep(0.5)
    await client.send_message(
        BOTLOG_CHATID,
        result,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("log", cmd) & filters.me)
async def set_log_p_m(client: Client, message: Message):
    if BOTLOG_CHATID != -100:
        # is_approved sekarang mengembalikan bool atau None.
        # Jika is_approved(chat_id) True, berarti saat ini tidak di-log (approved to NOT log).
        # Jadi, untuk "log" (mengaktifkan log), kita perlu "disapprove" (menghapus dari daftar nolog).
        if is_approved(message.chat.id):
            disapprove(message.chat.id) # Menggunakan fungsi disapprove yang dimigrasi
            await message.edit("**LOG Chat dari Grup ini Berhasil Diaktifkan**")
        else:
            await message.edit("**LOG Chat dari Grup ini Sudah Aktif**") # Pesan jika sudah aktif


@Client.on_message(filters.command("nolog", cmd) & filters.me)
async def set_no_log_p_m(client: Client, message: Message):
    if BOTLOG_CHATID != -100:
        # is_approved sekarang mengembalikan bool atau None.
        # Jika is_approved(chat_id) False atau None, berarti saat ini di-log.
        # Jadi, untuk "nolog" (mematikan log), kita perlu "approve" (menambahkan ke daftar nolog).
        if not is_approved(message.chat.id):
            approve(message.chat.id) # Menggunakan fungsi approve yang dimigrasi
            await message.edit("**LOG Chat dari Grup ini Berhasil Dimatikan**")
        else:
            await message.edit("**LOG Chat dari Grup ini Sudah Nonaktif**") # Pesan jika sudah nonaktif


@Client.on_message(filters.command(["pmlog", "pmlogger"], cmd) & filters.me)
async def set_pmlog(client: Client, message: Message):
    if BOTLOG_CHATID == -100:
        return await message.edit(
            "**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **di Config Vars**"
        )
    
    input_str = get_arg(message)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    else:
        return await edit_or_reply(message, "**Gunakan: `.pmlog on` atau `.pmlog off`**")

    # gvarstatus mengembalikan string "true", "false", atau None
    current_pmlog_status = gvarstatus("PMLOG")
    PMLOG_IS_ON = (current_pmlog_status != "false") # Dianggap aktif jika "true" atau None

    if PMLOG_IS_ON and h_type: # Sedang ON dan ingin set ON
        await edit_or_reply(message, "**PM LOG Sudah Diaktifkan**")
    elif not PMLOG_IS_ON and not h_type: # Sedang OFF dan ingin set OFF
        await edit_or_reply(message, "**PM LOG Sudah Dimatikan**")
    else: # Perubahan status
        addgvar("PMLOG", str(h_type).lower()) # Simpan sebagai "true" atau "false"
        if h_type:
            await edit_or_reply(message, "**PM LOG Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**PM LOG Berhasil Dimatikan**")


@Client.on_message(filters.command(["gruplog", "grouplog", "gclog"], cmd) & filters.me)
async def set_gruplog(client: Client, message: Message):
    if BOTLOG_CHATID == -100:
        return await message.edit(
            "**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **di Config Vars**"
        )
    
    input_str = get_arg(message)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    else:
        return await edit_or_reply(message, "**Gunakan: `.gruplog on` atau `.gruplog off`**")

    # gvarstatus mengembalikan string "true", "false", atau None
    current_gruplog_status = gvarstatus("GRUPLOG")
    GRUPLOG_IS_ON = (current_gruplog_status != "false") # Dianggap aktif jika "true" atau None

    if GRUPLOG_IS_ON and h_type: # Sedang ON dan ingin set ON
        await edit_or_reply(message, "**Group Log Sudah Diaktifkan**")
    elif not GRUPLOG_IS_ON and not h_type: # Sedang OFF dan ingin set OFF
        await edit_or_reply(message, "**Group Log Sudah Dimatikan**")
    else: # Perubahan status
        addgvar("GRUPLOG", str(h_type).lower()) # Simpan sebagai "true" atau "false"
        if h_type:
            await edit_or_reply(message, "**Group Log Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**Group Log Berhasil Dimatikan**")


add_command_help(
    "log",
    [
        [
            "log",
            "Untuk mengaktifkan Log Chat dari obrolan/grup itu.",
        ],
        [
            "nolog",
            "Untuk menonaktifkan Log Chat dari obrolan/grup itu.",
        ],
        [
            "pmlog on/off",
            "Untuk mengaktifkan atau menonaktifkan log pesan pribadi yang akan di forward ke grup log.",
        ],
        [
            "gruplog on/off",
            "Untuk mengaktifkan atau menonaktifkan tag grup, yang akan masuk ke grup log.",
        ],
    ],
)
