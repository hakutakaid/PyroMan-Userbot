# Credits: @mrismanaziz
# Copyright (C) 2022 Pyro-ManUserbot
#
# This file is a part of < https://github.com/mrismanaziz/PyroMan-Userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/mrismanaziz/PyroMan-Userbot/blob/main/LICENSE/>.
#
# t.me/SharingUserbot & t.me/Lunatic0de

import asyncio
import os
import time
from platform import python_version

from pyrogram import Client
from pyrogram import __version__ as versipyro
from pyrogram import filters
from pyrogram.types import Message
from telegraph import exceptions, upload_file

from config import BOT_VER, CHANNEL, CMD_HANDLER as cmd, GROUP
from ProjectMan import CMD_HELP, StartTime
from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.PyroHelpers import ReplyCheck
# Mengimpor langsung fungsi gvarstatus dan addgvar dari modul globals yang sudah dimigrasi
from ProjectMan.helpers.SQL.globals import gvarstatus, addgvar
from ProjectMan.helpers.tools import convert_to_image
from ProjectMan.utils import get_readable_time
from ProjectMan.utils.misc import restart

from .help import add_command_help

modules = CMD_HELP

# Mengambil nilai dari database menggunakan fungsi gvarstatus
# Fungsi gvarstatus sekarang akan mengembalikan string atau None jika tidak ditemukan
# Kita perlu memastikan nilai default jika gvarstatus mengembalikan None
alive_logo = gvarstatus("ALIVE_LOGO")
if alive_logo is None:
    alive_logo = "https://telegra.ph/file/9dc4e335feaaf6a214818.jpg"

emoji = gvarstatus("ALIVE_EMOJI")
if emoji is None:
    emoji = "⚡️"

alive_text = gvarstatus("ALIVE_TEKS_CUSTOM")
if alive_text is None:
    alive_text = "Hey, I am alive."


@Client.on_message(filters.command(["alive", "awake"], cmd) & filters.me)
async def alive(client: Client, message: Message):
    xx = await edit_or_reply(message, "⚡️")
    await asyncio.sleep(2)
    send = client.send_video if alive_logo.endswith(".mp4") else client.send_photo
    uptime = await get_readable_time((time.time() - StartTime))
    
    # Gunakan f-string untuk penulisan yang lebih bersih dan aman
    man = (
        f"**[PyroMan-Userbot](https://github.com/mrismanaziz/PyroMan-Userbot) is Up and Running.**\n\n"
        f"**{alive_text}**\n\n"
        f"{emoji} **Master :** {client.me.mention} \n"
        f"{emoji} **Modules :** `{len(modules)} Modules` \n"
        f"{emoji} **Bot Version :** `{BOT_VER}` \n"
        f"{emoji} **Python Version :** `{python_version()}` \n"
        f"{emoji} **Pyrogram Version :** `{versipyro}` \n"
        f"{emoji} **Bot Uptime :** `{uptime}` \n\n"
        f"    **[𝗦𝘂𝗽𝗽𝗼𝗿𝘁](https://t.me/{GROUP})** | **[𝗖𝗵𝗮𝗻𝗻𝗲𝗹](https://t.me/{CHANNEL})** | **[𝗢𝘄𝗻𝗲𝗿](tg://user?id={client.me.id})**"
    )
    
    try:
        await asyncio.gather(
            xx.delete(),
            send(
                message.chat.id,
                alive_logo,
                caption=man,
                reply_to_message_id=ReplyCheck(message),
            ),
        )
    except Exception: # Tangani Exception yang lebih umum jika BaseException tidak relevan
        await xx.edit(man, disable_web_page_preview=True)


@Client.on_message(filters.command("setalivelogo", cmd) & filters.me)
async def setalivelogo(client: Client, message: Message):
    # Tidak perlu lagi blok try...except AttributeError karena kita sudah mengimpor fungsi langsung
    Man = await edit_or_reply(message, "`Processing...`")
    link = None
    if len(message.command) > 1:
        link = message.text.split(None, 1)[1]
    
    if message.reply_to_message and message.reply_to_message.media:
        if message.reply_to_message.sticker:
            m_d = await convert_to_image(message, client)
        else:
            m_d = await message.reply_to_message.download()
        
        try:
            media_url = upload_file(m_d)
        except exceptions.TelegraphException as exc:
            await Man.edit(f"**ERROR:** `{exc}`")
            os.remove(m_d)
            return
        finally: # Pastikan file lokal dihapus meskipun ada error lain
            if os.path.exists(m_d):
                os.remove(m_d)
        
        link = f"https://telegra.ph/{media_url[0]}"
    
    if not link:
        return await Man.edit("**Mohon berikan link Telegraph atau balas ke foto/video/GIF!**")
        
    addgvar("ALIVE_LOGO", link) # Menggunakan fungsi addgvar yang sudah dimigrasi
    await Man.edit(
        f"**Berhasil Mengcustom ALIVE LOGO Menjadi** `{link}`",
        disable_web_page_preview=True,
    )
    restart()


@Client.on_message(filters.command("setalivetext", cmd) & filters.me)
async def setalivetext(client: Client, message: Message):
    # Tidak perlu lagi blok try...except AttributeError
    text = None
    if len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    
    if message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption
    
    Man = await edit_or_reply(message, "`Processing...`")
    
    if not text:
        return await Man.edit("**Berikan Sebuah Text atau Reply ke text**")
    
    addgvar("ALIVE_TEKS_CUSTOM", text) # Menggunakan fungsi addgvar yang sudah dimigrasi
    await Man.edit(f"**Berhasil Mengcustom ALIVE TEXT Menjadi** `{text}`")
    restart()


@Client.on_message(filters.command("setemoji", cmd) & filters.me)
async def setemoji(client: Client, message: Message):
    # Tidak perlu lagi blok try...except AttributeError
    emoji_val = None
    if len(message.command) > 1:
        emoji_val = message.text.split(None, 1)[1]
    
    Man = await edit_or_reply(message, "`Processing...`")
    
    if not emoji_val:
        return await Man.edit("**Berikan Sebuah Emoji**")
    
    addgvar("ALIVE_EMOJI", emoji_val) # Menggunakan fungsi addgvar yang sudah dimigrasi
    await Man.edit(f"**Berhasil Mengcustom EMOJI ALIVE Menjadi** {emoji_val}")
    restart()


add_command_help(
    "alive",
    [
        [
            "alive",
            "Untuk memeriksa userbot Anda berfungsi atau tidak",
        ],
        [
            "setalivelogo <link telegraph atau reply ke foto/video/gif>",
            "Untuk meng-custom alive logo userbot Anda",
        ],
        [
            "setalivetext <text>",
            "Untuk meng-custom alive text userbot Anda",
        ],
        [
            "setemoji <emoji>",
            "Untuk meng-custom emoji alive userbot Anda",
        ],
    ],
)
