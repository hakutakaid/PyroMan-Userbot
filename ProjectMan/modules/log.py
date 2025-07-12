# ProjectMan/modules/log.py

import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

# Hapus: from config import BOTLOG_CHATID
# Impor fungsi baru dari globals.py untuk mendapatkan BOTLOG_CHATID
from ProjectMan.helpers.SQL.globals import addgvar, gvarstatus, get_botlog_chat_id, set_botlog_chat_id

from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.SQL.no_log_pms_sql import is_approved, approve, disapprove

from ProjectMan.helpers.SQL.__init__ import LOGGER # Pastikan ini tetap ada
from ProjectMan.helpers.tools import get_arg
from config import CMD_HANDLER as cmd

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
    current_botlog_chat_id = get_botlog_chat_id()
    
    if current_botlog_chat_id is None:
        LOGGER(__name__).warning("BOTLOG_CHATID belum diatur di database, tidak dapat meneruskan log PM.")
        return
    
    pmlog_status = gvarstatus("PMLOG")
    if pmlog_status == "false":
        return

    if not is_approved(message.chat.id) and message.chat.id != 777000:
        if LOG_CHATS_.RECENT_USER != message.chat.id:
            LOG_CHATS_.RECENT_USER = message.chat.id
            if LOG_CHATS_.NEWPM:
                try:
                    # Catch the specific error here
                    await LOG_CHATS_.NEWPM.edit(
                        LOG_CHATS_.NEWPM.text.replace(
                            "**💌 #NEW_MESSAGE**",
                            f" • `{LOG_CHATS_.COUNT}` **Pesan**",
                        )
                    )
                except MessageNotModified:
                    # Log it if you want, or just pass silently
                    LOGGER(__name__).debug("Message not modified, skipping edit.")
                    pass
                except Exception as e: # Catch other unexpected errors during edit
                    LOGGER(__name__).error(f"Failed to edit previous PM log message: {e}")
                    pass
                finally: # Ensure count resets even if edit fails
                    LOG_CHATS_.COUNT = 0
            
            # This part sends the initial message, should be outside the NEWPM check
            LOG_CHATS_.NEWPM = await client.send_message(
                current_botlog_chat_id,
                f"💌 <b>#MENERUSKAN #PESAN_BARU</b>\n<b> • Dari :</b> {message.from_user.mention}\n<b> • User ID :</b> <code>{message.from_user.id}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        try:
            async for pmlog in client.search_messages(message.chat.id, limit=1):
                await pmlog.forward(current_botlog_chat_id)
            LOG_CHATS_.COUNT += 1
        except Exception as e:
            LOGGER(__name__).error(f"Failed to forward PM log: {e}")
            pass


@Client.on_message(filters.group & filters.mentioned & filters.incoming)
async def log_tagged_messages(client: Client, message: Message):
    # Ambil BOTLOG_CHATID dari database
    current_botlog_chat_id = get_botlog_chat_id()

    if current_botlog_chat_id is None: # Cek jika belum diatur di database
        LOGGER(__name__).warning("BOTLOG_CHATID belum diatur di database, tidak dapat meneruskan log grup.")
        return
    
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    gruplog_status = gvarstatus("GRUPLOG")
    if gruplog_status == "false":
        return

    # Periksa apakah chat_id disetujui untuk tidak di-log
    if is_approved(message.chat.id): # Hapus `or (current_botlog_chat_id == -100)`
        return
        
    result = f"<b>📨 #TAGS #MESSAGE</b>\n<b> • Dari : </b>{message.from_user.mention}"
    result += f"\n<b> • Grup : </b>{message.chat.title}"
    result += f"\n<b> • 👀 </b><a href = '{message.link}'>Lihat Pesan</a>"
    message_content = message.text if message.text else message.caption 
    if message_content:
        result += f"\n<b> • Message : </b><code>{message_content}</code>"
    
    await asyncio.sleep(0.5)
    await client.send_message(
        current_botlog_chat_id, # Gunakan BOTLOG_CHATID dari database
        result,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command("log", cmd) & filters.me)
async def set_log_p_m(client: Client, message: Message):
    # Ambil BOTLOG_CHATID dari database
    current_botlog_chat_id = get_botlog_chat_id()

    if current_botlog_chat_id is None: # Cek jika belum diatur di database
        return await message.edit(
            "**BOTLOG_CHATID belum diatur di database. Gunakan `.setlogchat <chat_id>` terlebih dahulu.**"
        )
    
    if is_approved(message.chat.id):
        disapprove(message.chat.id)
        await message.edit("**LOG Chat dari Grup ini Berhasil Diaktifkan**")
    else:
        await message.edit("**LOG Chat dari Grup ini Sudah Aktif**")


@Client.on_message(filters.command("nolog", cmd) & filters.me)
async def set_no_log_p_m(client: Client, message: Message):
    # Ambil BOTLOG_CHATID dari database
    current_botlog_chat_id = get_botlog_chat_id()

    if current_botlog_chat_id is None: # Cek jika belum diatur di database
        return await message.edit(
            "**BOTLOG_CHATID belum diatur di database. Gunakan `.setlogchat <chat_id>` terlebih dahulu.**"
        )
        
    if not is_approved(message.chat.id):
        approve(message.chat.id)
        await message.edit("**LOG Chat dari Grup ini Berhasil Dimatikan**")
    else:
        await message.edit("**LOG Chat dari Grup ini Sudah Nonaktif**")


@Client.on_message(filters.command(["pmlog", "pmlogger"], cmd) & filters.me)
async def set_pmlog(client: Client, message: Message):
    # Ambil BOTLOG_CHATID dari database
    current_botlog_chat_id = get_botlog_chat_id()

    if current_botlog_chat_id is None: # Cek jika belum diatur di database
        return await message.edit(
            "**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **dengan `.setlogchat <chat_id>`**"
        )
    
    input_str = get_arg(message)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    else:
        return await edit_or_reply(message, "**Gunakan: `.pmlog on` atau `.pmlog off`**")

    current_pmlog_status = gvarstatus("PMLOG")
    PMLOG_IS_ON = (current_pmlog_status != "false")

    if PMLOG_IS_ON and h_type:
        await edit_or_reply(message, "**PM LOG Sudah Diaktifkan**")
    elif not PMLOG_IS_ON and not h_type:
        await edit_or_reply(message, "**PM LOG Sudah Dimatikan**")
    else:
        addgvar("PMLOG", str(h_type).lower())
        if h_type:
            await edit_or_reply(message, "**PM LOG Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**PM LOG Berhasil Dimatikan**")


@Client.on_message(filters.command(["gruplog", "grouplog", "gclog"], cmd) & filters.me)
async def set_gruplog(client: Client, message: Message):
    # Ambil BOTLOG_CHATID dari database
    current_botlog_chat_id = get_botlog_chat_id()

    if current_botlog_chat_id is None: # Cek jika belum diatur di database
        return await message.edit(
            "**Untuk Menggunakan Module ini, Anda Harus Mengatur** `BOTLOG_CHATID` **dengan `.setlogchat <chat_id>`**"
        )
    
    input_str = get_arg(message)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    else:
        return await edit_or_reply(message, "**Gunakan: `.gruplog on` atau `.gruplog off`**")

    current_gruplog_status = gvarstatus("GRUPLOG")
    GRUPLOG_IS_ON = (current_gruplog_status != "false")

    if GRUPLOG_IS_ON and h_type:
        await edit_or_reply(message, "**Group Log Sudah Diaktifkan**")
    elif not GRUPLOG_IS_ON and not h_type:
        await edit_or_reply(message, "**Group Log Sudah Dimatikan**")
    else:
        addgvar("GRUPLOG", str(h_type).lower())
        if h_type:
            await edit_or_reply(message, "**Group Log Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**Group Log Berhasil Dimatikan**")


# Perintah baru untuk mengatur BOTLOG_CHATID dari dalam bot
@Client.on_message(filters.command("setlogchat", cmd) & filters.me)
async def set_botlog_chat(client: Client, message: Message):
    if not message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
        return await edit_or_reply(message, "**Gunakan perintah ini di grup atau channel yang ingin Anda jadikan grup log.**")

    # Kita bisa menggunakan message.chat.id untuk mendapatkan ID chat tempat perintah diketik
    # Atau jika ingin spesifik, pengguna bisa memberikan argumen chat_id
    chat_id_to_set = message.chat.id
    
    # Jika pengguna memberikan argumen, gunakan argumen tersebut
    arg = get_arg(message)
    if arg:
        try:
            # Coba konversi ke integer, jika gagal biarkan string (untuk username channel/group)
            chat_id_to_set = int(arg)
        except ValueError:
            chat_id_to_set = arg # Biarkan sebagai string jika itu username

    set_botlog_chat_id(chat_id_to_set)
    await edit_or_reply(
        message,
        f"**BOTLOG_CHATID berhasil diatur ke:** `{chat_id_to_set}`\n\nLog pesan dan tag akan dikirim ke sini."
    )


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
        [
            "setlogchat <chat_id/username>",
            "Untuk mengatur Chat ID atau Username Grup/Channel yang akan dijadikan Grup Log. (Gunakan di grup target atau dengan argumen ID)",
        ],
    ],
)