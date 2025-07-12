# ProjectMan/modules/broadcast.py

import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message

# Assuming config.py also has CMD_HANDLER and DEVS, but we remove BLACKLIST_GCAST import
from config import CMD_HANDLER as cmd
from ProjectMan.helpers.adminHelpers import DEVS
from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.tools import get_arg

# Import new DB functions
from ProjectMan.helpers.SQL.gcast_blacklist_db import (
    add_chat_to_blacklist,
    remove_chat_from_blacklist,
    get_gcast_blacklist,
)

from .help import add_command_help

# Remove the old blacklist loading logic from GitHub


@Client.on_message(filters.command("gcast", cmd) & filters.me)
async def gcast_cmd(client: Client, message: Message):
    if message.reply_to_message:
        msg = message.reply_to_message
    elif get_arg(message):
        msg = get_arg(message)
    else:
        return await message.edit_text("**Berikan Sebuah Pesan atau Reply**")
    
    Man = await edit_or_reply(message, "`Started global broadcast...`")
    
    current_blacklist = get_gcast_blacklist() # Get blacklist from DB
    done = 0
    error = 0
    
    async for dialog in client.get_dialogs():
        if dialog.chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
            chat = dialog.chat.id
            if chat not in current_blacklist: # Check against DB blacklist
                try:
                    if message.reply_to_message:
                        await msg.copy(chat)
                    else: # Assuming get_arg provides the text directly for send_message
                        await client.send_message(chat, msg)
                    done += 1
                    await asyncio.sleep(0.3)
                except Exception:
                    error += 1
                    await asyncio.sleep(0.3)
    await Man.edit_text(
        f"**Berhasil Mengirim Pesan Ke** `{done}` **Grup, Gagal Mengirim Pesan Ke** `{error}` **Grup**"
    )


@Client.on_message(filters.command("gucast", cmd) & filters.me)
async def gucast_cmd(client: Client, message: Message):
    if message.reply_to_message:
        msg = message.reply_to_message
    elif get_arg(message):
        msg = get_arg(message)
    else:
        return await message.edit_text("**Berikan Sebuah Pesan atau Reply**")
    
    Man = await edit_or_reply(message, "`Started global broadcast...`")
    done = 0
    error = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type == enums.ChatType.PRIVATE and not dialog.chat.is_verified:
            chat = dialog.chat.id
            if chat not in DEVS:
                try:
                    if message.reply_to_message:
                        await msg.copy(chat)
                    else: # Assuming get_arg provides the text directly for send_message
                        await client.send_message(chat, msg)
                    done += 1
                    await asyncio.sleep(0.3)
                except Exception:
                    error += 1
                    await asyncio.sleep(0.3)
    await Man.edit_text(
        f"**Berhasil Mengirim Pesan Ke** `{done}` **chat, Gagal Mengirim Pesan Ke** `{error}` **chat**"
    )


@Client.on_message(filters.command("blchat", cmd) & filters.me)
async def blchatgcast(client: Client, message: Message):
    current_blacklist = get_gcast_blacklist()
    if current_blacklist:
        # Format the list nicely, converting integers to strings for display
        list_str = "\n» ".join(str(chat_id) for chat_id in current_blacklist)
        await edit_or_reply(
            message,
            f"🔮 **Blacklist GCAST:** `Enabled`\n\n📚 **Blacklist Group:**\n» {list_str}\n\nKetik `{cmd}addblacklist` di grup yang ingin anda tambahkan ke daftar blacklist gcast.",
        )
    else:
        await edit_or_reply(message, "🔮 **Blacklist GCAST:** `Disabled`\n\nTidak ada grup dalam daftar blacklist.")


@Client.on_message(filters.command("addblacklist", cmd) & filters.me)
async def addblacklist(client: Client, message: Message):
    xxnx = await edit_or_reply(message, "`Processing...`")
    chat_id_to_add = message.chat.id

    if add_chat_to_blacklist(chat_id_to_add):
        await xxnx.edit(
            f"**Berhasil Menambahkan** `{chat_id_to_add}` **ke daftar blacklist gcast.**"
        )
    else:
        await xxnx.edit(
            f"**Grup** `{chat_id_to_add}` **sudah ada dalam daftar blacklist gcast.**"
        )


@Client.on_message(filters.command("delblacklist", cmd) & filters.me)
async def delblacklist(client: Client, message: Message):
    xxnx = await edit_or_reply(message, "`Processing...`")
    chat_id_to_remove = message.chat.id

    if remove_chat_from_blacklist(chat_id_to_remove):
        await xxnx.edit(
            f"**Berhasil Menghapus** `{chat_id_to_remove}` **dari daftar blacklist gcast.**"
        )
    else:
        await xxnx.edit("**Grup ini tidak ada dalam daftar blacklist gcast.**")


add_command_help(
    "broadcast",
    [
        [
            "gcast <text/reply>",
            "Mengirim Global Broadcast pesan ke Seluruh Grup yang kamu masuk. (Bisa Mengirim Media/Sticker)",
        ],
        [
            "gucast <text/reply>",
            "Mengirim Global Broadcast pesan ke Seluruh Private Massage / PC yang masuk. (Bisa Mengirim Media/Sticker)",
        ],
        [
            "blchat",
            "Untuk Mengecek informasi daftar blacklist gcast.",
        ],
        [
            "addblacklist",
            "Untuk Menambahkan grup tersebut ke blacklist gcast.",
        ],
        [
            "delblacklist",
            f"Untuk Menghapus grup tersebut dari blacklist gcast.\n\n  •  **Note : **Ketik perintah** `{cmd}addblacklist` **dan** `{cmd}delblacklist` **di grup yang kamu Blacklist.",
        ],
    ],
)
