# Credits: @mrismanaziz
# Copyright (C) 2022 Pyro-ManUserbot
#
# This file is a part of < https://github.com/mrismanaziz/PyroMan-Userbot/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/mrismanaziz/PyroMan-Userbot/blob/main/LICENSE/>.
#
# t.me/SharingUserbot & t.me/Lunatic0de

from pyrogram import Client, errors, filters
from pyrogram.types import ChatPermissions, Message

from config import CMD_HANDLER as cmd
from ProjectMan import LOGS # Pastikan LOGS diimpor dengan benar dari ProjectMan
from ProjectMan.helpers.adminHelpers import DEVS, WHITELIST
from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.PyroHelpers import get_ub_chats
from ProjectMan.utils import extract_user, extract_user_and_reason

# Mengimpor langsung fungsi dari modul gban_sql dan gmute_sql yang sudah dimigrasi
# Tidak perlu lagi importlib dan try-except AttributeError
from ProjectMan.helpers.SQL.gban_sql import gban, ungban, is_gbanned, gbanned_users
from ProjectMan.helpers.SQL.gmute_sql import gmute, ungmute, is_gmuted, gmuted_users
from ProjectMan.modules.help import add_command_help

# Variabel global untuk menampung fungsi-fungsi dari modul SQL.
# Sekarang langsung menunjuk ke fungsi yang diimpor.
sql = None
sql2 = None

def globals_init():
    global sql, sql2
    try:
        # Langsung menunjuk ke fungsi yang diimpor
        # Kita tidak lagi mengimpor modul secara keseluruhan, tetapi fungsi spesifik
        sql = __import__("ProjectMan.helpers.SQL.gban_sql") # Hanya untuk tujuan referensi di sini
        sql2 = __import__("ProjectMan.helpers.SQL.gmute_sql") # Hanya untuk tujuan referensi di sini

        # Jika kita mengimpor fungsi satu per satu di awal,
        # kita tidak perlu variabel 'sql' dan 'sql2' ini lagi.
        # Saya akan membiarkan variabel global tetap ada seperti kode asli,
        # tetapi penggunaannya akan mengacu pada fungsi yang sudah diimpor.
        pass
    except Exception as e:
        # Ini akan menangkap jika ada masalah dengan impor dasar,
        # tetapi tidak lagi untuk kasus "Non-SQL mode" karena kita berasumsi SQL ada.
        LOGS.error(f"Failed to initialize global SQL modules: {e}")
        raise # Tetap naikkan error jika ada masalah serius


globals_init()


@Client.on_message(
    filters.command("cgban", ["."]) & filters.user(DEVS) & ~filters.via_bot
)
@Client.on_message(filters.command("gban", cmd) & filters.me)
async def gban_user(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    if message.from_user.id != client.me.id:
        Man = await message.reply("`Gbanning...`")
    else:
        Man = await message.edit("`Gbanning....`")
    if not user_id:
        return await Man.edit("Saya tidak dapat menemukan pengguna itu.")
    if user_id == client.me.id:
        return await Man.edit("**Ngapain NgeGban diri sendiri Goblok 🐽**")
    if user_id in DEVS:
        return await Man.edit("**Gagal GBAN karena dia adalah Pembuat saya 🗿**")
    if user_id in WHITELIST:
        return await Man.edit(
            "**Gagal GBAN karena dia adalah admin @SharingUserbot 🗿**"
        )
    if user_id:
        try:
            user = await client.get_users(user_id)
        except Exception:
            return await Man.edit("`Harap tentukan pengguna yang valid!`")

    if is_gbanned(user.id): # Menggunakan fungsi is_gbanned yang diimpor langsung
        return await Man.edit(
            f"[Jamet](tg://user?id={user.id}) **ini sudah ada di daftar gbanned**"
        )
    f_chats = await get_ub_chats(client)
    if not f_chats:
        return await Man.edit("**Anda tidak mempunyai GC yang anda admin 🥺**")
    er = 0
    done = 0
    for gokid in f_chats:
        try:
            await client.ban_chat_member(chat_id=gokid, user_id=int(user.id))
            done += 1
        except Exception: # Mengganti BaseException dengan Exception untuk lebih spesifik
            er += 1
    gban(user.id) # Menggunakan fungsi gban yang diimpor langsung
    msg = (
        r"**\\#GBanned_User//**"
        f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})"
        f"\n**User ID:** `{user.id}`"
    )
    if reason:
        msg += f"\n**Reason:** `{reason}`"
    msg += f"\n**Affected To:** `{done}` **Chats**"
    await Man.edit(msg)


@Client.on_message(
    filters.command("cungban", ["."]) & filters.user(DEVS) & ~filters.via_bot
)
@Client.on_message(filters.command("ungban", cmd) & filters.me)
async def ungban_user(client: Client, message: Message):
    user_id, reason = await extract_user_and_reason(message, sender_chat=True)
    if message.from_user.id != client.me.id:
        Man = await message.reply("`UnGbanning...`")
    else:
        Man = await message.edit("`UnGbanning....`")
    if not user_id:
        return await Man.edit("Saya tidak dapat menemukan pengguna itu.")
    if user_id:
        try:
            user = await client.get_users(user_id)
        except Exception:
            return await Man.edit("`Harap tentukan pengguna yang valid!`")

    try:
        if not is_gbanned(user.id): # Menggunakan fungsi is_gbanned yang diimpor langsung
            return await Man.edit("`User already ungban`")
        ung_chats = await get_ub_chats(client)
        if not ung_chats:
            return await Man.edit("**Anda tidak mempunyai GC yang anda admin 🥺**")
        er = 0
        done = 0
        for good_boi in ung_chats:
            try:
                await client.unban_chat_member(chat_id=good_boi, user_id=user.id)
                done += 1
            except Exception: # Mengganti BaseException dengan Exception untuk lebih spesifik
                er += 1
        ungban(user.id) # Menggunakan fungsi ungban yang diimpor langsung
        msg = (
            r"**\\#UnGbanned_User//**"
            f"\n\n**First Name:** [{user.first_name}](tg://user?id={user.id})"
            f"\n**User ID:** `{user.id}`"
        )
        if reason:
            msg += f"\n**Reason:** `{reason}`"
        msg += f"\n**Affected To:** `{done}` **Chats**"
        await Man.edit(msg)
    except Exception as e:
        await Man.edit(f"**ERROR:** `{e}`")
        return


@Client.on_message(filters.command("listgban", cmd) & filters.me)
async def gbanlist(client: Client, message: Message):
    users = gbanned_users() # Menggunakan fungsi gbanned_users yang diimpor langsung
    Man = await edit_or_reply(message, "`Processing...`")
    if not users:
        return await Man.edit("Belum ada Pengguna yang Di-Gban")
    gban_list = "**GBanned Users:**\n"
    count = 0
    for i in users:
        # 'i' sekarang adalah string (user_id) karena gbanned_users mengembalikan list[str]
        # dari migrasi gban_sql.py. Tidak ada atribut 'sender' lagi.
        count += 1
        gban_list += f"**{count} -** `{i}`\n"
    return await Man.edit(gban_list)


@Client.on_message(filters.command("gmute", cmd) & filters.me)
async def gmute_user(client: Client, message: Message):
    args = await extract_user(message)
    reply = message.reply_to_message
    Man = await edit_or_reply(message, "`Processing...`")
    if args:
        try:
            user = await client.get_users(args)
        except Exception:
            await Man.edit(f"`Harap tentukan pengguna yang valid!`")
            return
    elif reply:
        user_id = reply.from_user.id
        user = await client.get_users(user_id)
    else:
        await Man.edit(f"`Harap tentukan pengguna yang valid!`")
        return
    if user.id == client.me.id:
        return await Man.edit("**Ngapain NgeGmute diri sendiri Goblok 🐽**")
    if user.id in DEVS:
        return await Man.edit("**Gagal GMUTE karena dia adalah Pembuat saya 🗿**")
    if user.id in WHITELIST:
        return await Man.edit(
            "**Gagal GMUTE karena dia adalah admin @SharingUserbot 🗿**"
        )
    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return await Man.edit("`Calm down anybob, you can't gmute yourself.`")
    except Exception: # Mengganti BaseException dengan Exception
        pass

    try:
        if is_gmuted(user.id): # Menggunakan fungsi is_gmuted yang diimpor langsung
            return await Man.edit("`User already gmuted`")
        gmute(user.id) # Menggunakan fungsi gmute yang diimpor langsung
        await Man.edit(f"[{user.first_name}](tg://user?id={user.id}) globally gmuted!")
        try:
            common_chats = await client.get_common_chats(user.id)
            for i in common_chats:
                await i.restrict_member(user.id, ChatPermissions())
        except Exception: # Mengganti BaseException dengan Exception
            pass
    except Exception as e:
        await Man.edit(f"**ERROR:** `{e}`")
        return


@Client.on_message(filters.command("ungmute", cmd) & filters.me)
async def ungmute_user(client: Client, message: Message):
    args = await extract_user(message)
    reply = message.reply_to_message
    Man = await edit_or_reply(message, "`Processing...`")
    if args:
        try:
            user = await client.get_users(args)
        except Exception:
            await Man.edit(f"`Harap tentukan pengguna yang valid!`")
            return
    elif reply:
        user_id = reply.from_user.id
        user = await client.get_users(user_id)
    else:
        await Man.edit(f"`Harap tentukan pengguna yang valid!`")
        return

    try:
        replied_user = reply.from_user
        if replied_user.is_self:
            return await Man.edit("`Calm down anybob, you can't ungmute yourself.`")
    except Exception: # Mengganti BaseException dengan Exception
        pass

    try:
        if not is_gmuted(user.id): # Menggunakan fungsi is_gmuted yang diimpor langsung
            return await Man.edit("`User already ungmuted`")
        ungmute(user.id) # Menggunakan fungsi ungmute yang diimpor langsung
        try:
            common_chats = await client.get_common_chats(user.id)
            for i in common_chats:
                await i.unban_member(user.id)
        except Exception: # Mengganti BaseException dengan Exception
            pass
        await Man.edit(
            f"[{user.first_name}](tg://user?id={user.id}) globally ungmuted!"
        )
    except Exception as e:
        await Man.edit(f"**ERROR:** `{e}`")
        return


@Client.on_message(filters.command("listgmute", cmd) & filters.me)
async def gmutelist(client: Client, message: Message):
    users = gmuted_users() # Menggunakan fungsi gmuted_users yang diimpor langsung
    Man = await edit_or_reply(message, "`Processing...`")
    if not users:
        return await Man.edit("Belum ada Pengguna yang Di-Gmute")
    gmute_list = "**GMuted Users:**\n"
    count = 0
    for i in users:
        # 'i' sekarang adalah string (sender) karena gmuted_users mengembalikan list[str]
        # dari migrasi gmute_sql.py. Tidak ada atribut 'sender' lagi.
        count += 1
        gmute_list += f"**{count} -** `{i}`\n"
    return await Man.edit(gmute_list)


@Client.on_message(filters.incoming & filters.group)
async def globals_check(client: Client, message: Message):
    if not message:
        return
    if not message.from_user:
        return
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not user_id:
        return
    if is_gbanned(user_id): # Menggunakan fungsi is_gbanned yang diimpor langsung
        try:
            await client.ban_chat_member(chat_id, user_id)
        except Exception: # Mengganti BaseException dengan Exception
            pass

    if is_gmuted(user_id): # Menggunakan fungsi is_gmuted yang diimpor langsung
        try:
            await message.delete()
        except errors.RPCError:
            pass # RPCError spesifik Pyrogram bisa dibiarkan tanpa logging tambahan jika sudah ditangani oleh Pyrogram sendiri
        try:
            await client.restrict_chat_member(chat_id, user_id, ChatPermissions())
        except Exception: # Mengganti BaseException dengan Exception
            pass

    message.continue_propagation()


add_command_help(
    "globals",
    [
        [
            "gban <reply/username/userid>",
            "Melakukan Global Banned Ke Semua Grup Dimana anda Sebagai Admin.",
        ],
        ["ungban <reply/username/userid>", "Membatalkan Global Banned."],
        ["listgban", "Menampilkan List Global Banned."],
    ],
)
