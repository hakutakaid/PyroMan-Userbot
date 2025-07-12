# Credits: @mrismanaziz
# Copyright (C) 2022 Pyro-ManUserbot
#
# This file is a part of < https://github.com/mrismanaziz/PyroMan-Userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/mrismanaziz/PyroMan-Userbot/blob/main/LICENSE/>.
#
# t.me/SharingUserbot & t.me/Lunatic0de

import time

from pyrogram import Client, filters
from pyrogram.types import Message

from config import CMD_HANDLER as cmd, BOTLOG_CHATID # Mengimpor BOTLOG_CHATID dari config jika belum
from ProjectMan import BOTLOG_CHATID # Menggunakan BOTLOG_CHATID yang sudah didefinisikan
from ProjectMan.helpers.msg_types import Types, get_message_type
from ProjectMan.helpers.parser import escape_markdown, mention_markdown
from ProjectMan.helpers.SQL.afk_db import get_afk, set_afk # Ini tetap sama karena fungsi DB sudah dimigrasi
from ProjectMan.modules.help import add_command_help

# Set priority to 11 and 12
MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 3  # seconds


@Client.on_message(filters.me & filters.command("afk", cmd))
async def afk(client: Client, message: Message):
    # Pastikan perintah afk_db.set_afk() menerima argumen yang benar
    # message.text.split(None, 1)[1] akan memberikan alasan jika ada
    if len(message.text.split()) >= 2:
        reason = message.text.split(None, 1)[1]
        set_afk(True, reason)
        await message.edit(
            "❏ {} **Telah AFK!**\n└ **Karena:** `{}`".format(
                mention_markdown(message.from_user.id, message.from_user.first_name),
                escape_markdown(reason), # Gunakan escape_markdown untuk alasan
            )
        )
    else:
        set_afk(True, "")
        await message.edit(
            "✘ {} **Telah AFK** ✘".format(
                mention_markdown(message.from_user.id, message.from_user.first_name)
            )
        )
    await message.stop_propagation()


@Client.on_message(
    (filters.mentioned | filters.private) & filters.incoming & ~filters.bot, group=11
)
async def afk_mentioned(client: Client, message: Message):
    global MENTIONED
    global AFK_RESTIRECT

    get = get_afk() # Memanggil fungsi dari afk_db.py yang sudah dimigrasi
    if get and get["afk"]:
        # Pyrogram secara otomatis menangani ID grup sebagai integer negatif.
        # Konversi ke string untuk konsistensi dengan penyimpanan jika diperlukan,
        # tetapi biasanya lebih baik bekerja dengan int secara langsung jika itu ID chat.
        # Jika Anda yakin ID chat di DB disimpan sebagai string tanpa `-100`, maka konversi ini perlu.
        # Kalau tidak, biarkan sebagai int. Asumsi Anda menyimpan ID chat di DB sebagai TEXT dari int.
        cid = str(message.chat.id).replace("-100", "") if "-" in str(message.chat.id) else str(message.chat.id)
        cid_int = message.chat.id # Gunakan integer asli untuk perbandingan waktu

        if cid_int in AFK_RESTIRECT:
            if int(AFK_RESTIRECT[cid_int]) >= int(time.time()):
                return
        AFK_RESTIRECT[cid_int] = int(time.time()) + DELAY_TIME # Gunakan cid_int sebagai kunci

        reason = get["reason"] if get["reason"] else "Alasan tidak diberikan." # Tangani alasan kosong

        if reason:
            await message.reply(
                "❏ {} **Sedang AFK!**\n└ **Karena:** `{}`".format(
                    client.me.mention, escape_markdown(reason) # Escape reason untuk markdown
                )
            )
        else:
            await message.reply(
                f"**Maaf** {client.me.first_name} **Sedang AFK!**"
            )

        # Pastikan text diambil dengan benar dari message (teks atau caption)
        message_content = ""
        if message.text:
            message_content = message.text
        elif message.caption:
            message_content = message.caption
        elif get_message_type(message)[1] != Types.TEXT: # Jika bukan teks/caption, gunakan nama tipe
            message_content = get_message_type(message)[1].name

        MENTIONED.append(
            {
                "user": message.from_user.first_name,
                "user_id": message.from_user.id,
                "chat": message.chat.title,
                "chat_id": cid, # tetap pakai yang sudah diproses untuk logging link
                "text": message_content,
                "message_id": message.id,
            }
        )
        try:
            await client.send_message(
                BOTLOG_CHATID,
                "**#MENTION**\n • **Dari :** {}\n • **Grup :** `{}`\n • **Pesan :** `{}`".format(
                    message.from_user.mention,
                    escape_markdown(message.chat.title), # Escape chat title
                    escape_markdown(message_content[:3500]), # Escape pesan
                ),
            )
        except Exception as e: # Tangani exception spesifik daripada BaseException
            LOGGER(__name__).error(f"Gagal mengirim log mention ke BOTLOG_CHATID: {e}")


@Client.on_message(filters.me & filters.group, group=12)
async def no_longer_afk(client: Client, message: Message):
    global MENTIONED
    global AFK_RESTIRECT

    get = get_afk() # Memanggil fungsi dari afk_db.py yang sudah dimigrasi
    if get and get["afk"]:
        set_afk(False, "") # Mengatur AFK ke False melalui fungsi DB
        try:
            await client.send_message(BOTLOG_CHATID, "**Anda sudah tidak lagi AFK!**")
        except Exception as e:
            LOGGER(__name__).error(f"Gagal mengirim pesan tidak AFK ke BOTLOG_CHATID: {e}")
            pass # Lanjutkan eksekusi meskipun gagal kirim log

        if MENTIONED: # Hanya kirim log mention jika ada mention
            text = "**Total {} Mention Saat Sedang AFK**\n".format(len(MENTIONED))
            for x in MENTIONED:
                msg_text_display = x["text"]
                if len(msg_text_display) >= 11: # Perbaiki ini menjadi 500 atau lebih jika ingin lebih panjang
                    msg_text_display = "{}...".format(msg_text_display[:500]) # Batasi teks untuk display

                # Pastikan format link benar dan semua bagian di-escape markdown
                text += "- [{}](https://t.me/c/{}/{}) ({}): `{}`\n".format(
                    escape_markdown(x["user"]),
                    x["chat_id"], # chat_id harus berupa string tanpa "-100" untuk link t.me/c
                    x["message_id"],
                    escape_markdown(x["chat"]), # Escape nama chat
                    escape_markdown(msg_text_display), # Escape teks pesan
                )
            try:
                await client.send_message(BOTLOG_CHATID, text)
            except Exception as e:
                LOGGER(__name__).error(f"Gagal mengirim ringkasan mention AFK ke BOTLOG_CHATID: {e}")
                pass
        MENTIONED = []
        AFK_RESTIRECT = {} # Reset restriksi AFK saat tidak AFK lagi

# Helper untuk menambahkan perintah bantuan (sesuai struktur ProjectMan Anda)
add_command_help(
    "afk",
    [
        [
            "afk <alasan>",
            "Memberi tahu orang yang menandai atau membalas salah satu pesan atau dm Anda kalau Anda sedang AFK.",
        ],
    ],
)
