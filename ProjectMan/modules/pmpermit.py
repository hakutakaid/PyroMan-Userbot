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
# Asumsi IntegrityError tidak lagi dari SQLAlchemy, tetapi mungkin dari sqlite3 jika ada constraint,
# atau bisa dihapus jika tidak ada penanganan khusus yang diperlukan untuk error tersebut di sini.
# Untuk keamanan, kita biarkan saja atau ganti dengan Exception umum.
# from sqlalchemy.exc import IntegrityError # Ini tidak diperlukan lagi

from config import CMD_HANDLER as cmd
from ProjectMan import TEMP_SETTINGS
from ProjectMan.helpers.adminHelpers import DEVS
from ProjectMan.helpers.basic import edit_or_reply
# Mengimpor langsung fungsi dari modul globals yang sudah dimigrasi
from ProjectMan.helpers.SQL.globals import addgvar, gvarstatus, delgvar # Tambahkan delgvar
# Mengimpor langsung fungsi dari modul pm_permit_sql yang sudah dimigrasi
from ProjectMan.helpers.SQL.pm_permit_sql import is_approved, approve, dissprove # Perbaiki dissprove ke disapprove jika itu namanya
from ProjectMan.helpers.tools import get_arg

from .help import add_command_help

DEF_UNAPPROVED_MSG = (
    "╔════════════════════╗\n"
    "     ⛑ 𝗔𝗧𝗧𝗘𝗡𝗧𝗜𝗢𝗡 𝗣𝗟𝗘𝗔𝗦𝗘 ⛑\n"
    "╚════════════════════╝\n"
    "• Saya belum menyetujui anda untuk PM.\n"
    "• Tunggu sampai saya menyetujui PM anda.\n"
    "• Jangan Spam Chat atau anda akan otomatis diblokir.\n"
    "╔════════════════════╗\n"
    "    𝗣𝗲𝘀𝗮𝗻 𝗢𝘁𝗼𝗺𝗮𝘁𝗶𝘀 𝗕𝘆 -𝗨𝘀𝗲𝗿𝗕𝗼𝘁\n"
    "╚════════════════════╝\n"
)


@Client.on_message(
    ~filters.me & filters.private & ~filters.bot & filters.incoming, group=69
)
async def incomingpm(client: Client, message: Message):
    # Tidak perlu lagi try-except untuk import di sini
    # from ProjectMan.helpers.SQL.globals import gvarstatus # Sudah diimpor di atas
    # from ProjectMan.helpers.SQL.pm_permit_sql import is_approved # Sudah diimpor di atas

    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return

    # auto_accept harus dipanggil dengan await
    if await auto_accept(client, message) or message.from_user.is_self:
        message.continue_propagation()
        return # Penting: keluar setelah continue_propagation jika kondisi terpenuhi

    if message.chat.id != 777000:
        # PM_LIMIT dari gvarstatus akan mengembalikan string atau None, konversi ke int
        pm_limit_str = gvarstatus("PM_LIMIT")
        PM_LIMIT = int(pm_limit_str) if pm_limit_str and pm_limit_str.isnumeric() else 5

        getmsg = gvarstatus("unapproved_msg")
        UNAPPROVED_MSG = getmsg if getmsg is not None else DEF_UNAPPROVED_MSG

        # is_approved sekarang mengembalikan boolean atau None
        apprv = is_approved(message.chat.id)
        if not apprv and message.text != UNAPPROVED_MSG:
            if message.chat.id not in TEMP_SETTINGS: # Pastikan kunci ada
                TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = "" # Inisialisasi
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] = 0 # Inisialisasi

            if TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] != message.text: # Hanya balas jika pesan berbeda
                # Hapus pesan PMPERMIT sebelumnya dari bot jika ada
                async for prev_bot_msg in client.search_messages(
                    message.chat.id,
                    from_user="me",
                    limit=10,
                    query=UNAPPROVED_MSG, # Cari berdasarkan teks pesan
                ):
                    try:
                        await prev_bot_msg.delete()
                    except Exception:
                        pass # Abaikan jika tidak bisa dihapus

                if TEMP_SETTINGS["PM_COUNT"][message.chat.id] < (int(PM_LIMIT) - 1):
                    ret = await message.reply_text(UNAPPROVED_MSG)
                    if ret:
                        TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ret.text
                
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] += 1
            
            if TEMP_SETTINGS["PM_COUNT"][message.chat.id] >= PM_LIMIT: # Gunakan >= PM_LIMIT
                await message.reply("**Maaf anda Telah Di Blokir Karna Spam Chat**")
                try:
                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except Exception: # Ganti BaseException dengan Exception
                    pass

                await client.block_user(message.chat.id)

    message.continue_propagation()


async def auto_accept(client: Client, message: Message):
    # Tidak perlu lagi try-except untuk import di sini
    # from ProjectMan.helpers.SQL.pm_permit_sql import approve, is_approved # Sudah diimpor di atas

    if message.chat.id in DEVS:
        try:
            approve(message.chat.id) # Memanggil fungsi approve yang sudah dimigrasi
            await client.send_message(
                message.chat.id,
                f"<b>Menerima Pesan!!!</b>\n{message.from_user.mention} <b>Terdeteksi Developer PyroMan-Userbot</b>",
                parse_mode=enums.ParseMode.HTML,
            )
            return True # Langsung return True karena sudah diapprove
        except Exception as e: # Tangani exception umum jika IntegrityError tidak lagi relevan
            # Log error jika ada masalah saat approve
            LOGGER(__name__).error(f"Error in auto_accept for DEVS: {e}")
            pass # Lanjutkan eksekusi meskipun approve gagal

    if message.chat.id not in [client.me.id, 777000]:
        if is_approved(message.chat.id): # Memanggil fungsi is_approved yang sudah dimigrasi
            return True

        # Ambil pesan terbaru dari bot (self) di chat tersebut
        async for msg in client.get_chat_history(message.chat.id, limit=1):
            if msg.from_user.id == client.me.id:
                try:
                    # Inisialisasi PM_COUNT dan PM_LAST_MSG jika belum ada
                    if message.chat.id not in TEMP_SETTINGS:
                        TEMP_SETTINGS["PM_COUNT"][message.chat.id] = 0
                        TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ""

                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except Exception: # Ganti BaseException dengan Exception
                    pass

                try:
                    approve(message.chat.id) # Memanggil fungsi approve yang sudah dimigrasi
                    # Hapus pesan UNAPPROVED_MSG yang dikirim oleh bot
                    async for unapproved_msg_del in client.search_messages(
                        message.chat.id,
                        from_user="me",
                        limit=10,
                        query=UNAPPROVED_MSG,
                    ):
                        try:
                            await unapproved_msg_del.delete()
                        except Exception:
                            pass # Abaikan jika tidak bisa dihapus
                    return True
                except Exception as e: # Ganti BaseException dengan Exception
                    # Log error jika ada masalah saat approve
                    LOGGER(__name__).error(f"Error in auto_accept after userbot reply: {e}")
                    pass

    return False


@Client.on_message(
    filters.command(["ok", "setuju", "approve"], cmd) & filters.me & filters.private
)
async def approvepm(client: Client, message: Message):
    # Tidak perlu lagi try-except untuk import dan pengecekan "Non-SQL mode"
    # from ProjectMan.helpers.SQL.pm_permit_sql import approve # Sudah diimpor di atas

    if message.reply_to_message:
        reply = message.reply_to_message
        replied_user = reply.from_user
        if replied_user.is_self:
            await message.edit("Anda tidak dapat menyetujui diri sendiri.")
            return
        aname = replied_user
        uid = replied_user.id
        name0 = str(replied_user.first_name)
    else:
        aname = message.chat
        if not aname.type == enums.ChatType.PRIVATE:
            await message.edit(
                "Saat ini Anda tidak sedang dalam PM dan Anda belum membalas pesan seseorang."
            )
            return
        uid = aname.id
        name0 = aname.first_name

    try:
        approve(uid) # Memanggil fungsi approve yang sudah dimigrasi
        await message.edit(f"**Menerima Pesan Dari** [{name0}](tg://user?id={uid})!")
        # Reset PM_COUNT dan PM_LAST_MSG setelah disetujui secara manual
        if uid in TEMP_SETTINGS["PM_COUNT"]:
            del TEMP_SETTINGS["PM_COUNT"][uid]
        if uid in TEMP_SETTINGS["PM_LAST_MSG"]:
            del TEMP_SETTINGS["PM_LAST_MSG"][uid]
        # Hapus pesan UNAPPROVED_MSG yang dikirim oleh bot
        async for unapproved_msg_del in client.search_messages(
            uid,
            from_user="me",
            limit=10,
            query=UNAPPROVED_MSG, # Gunakan variabel UNAPPROVED_MSG global
        ):
            try:
                await unapproved_msg_del.delete()
            except Exception:
                pass

    except Exception: # Mengganti IntegrityError dengan Exception, atau biarkan IntegrityError jika Anda ingin menangani spesifik
        await message.edit(
            f"[{name0}](tg://user?id={uid}) mungkin sudah disetujui untuk PM."
        )
        return


@Client.on_message(
    filters.command(["tolak", "nopm", "disapprove"], cmd) & filters.me & filters.private
)
async def disapprovepm(client: Client, message: Message):
    # Tidak perlu lagi try-except untuk import dan pengecekan "Non-SQL mode"
    # from ProjectMan.helpers.SQL.pm_permit_sql import dissprove # Sudah diimpor di atas

    if message.reply_to_message:
        reply = message.reply_to_message
        replied_user = reply.from_user
        if replied_user.is_self:
            await message.edit("Anda tidak bisa menolak dirimu sendiri.")
            return
        aname = replied_user
        uid = replied_user.id
        name0 = str(replied_user.first_name)
    else:
        aname = message.chat
        if not aname.type == enums.ChatType.PRIVATE:
            await message.edit(
                "Saat ini Anda tidak sedang dalam PM dan Anda belum membalas pesan seseorang."
            )
            return
        uid = aname.id
        name0 = aname.first_name

    dissprove(uid) # Memanggil fungsi dissprove yang sudah dimigrasi

    await message.edit(
        f"**Pesan** [{name0}](tg://user?id={uid}) **Telah Ditolak, Mohon Jangan Melakukan Spam Chat!**"
    )
    # Hapus juga dari TEMP_SETTINGS jika ada
    if uid in TEMP_SETTINGS["PM_COUNT"]:
        del TEMP_SETTINGS["PM_COUNT"][uid]
    if uid in TEMP_SETTINGS["PM_LAST_MSG"]:
        del TEMP_SETTINGS["PM_LAST_MSG"][uid]


@Client.on_message(filters.command("pmlimit", cmd) & filters.me)
async def setpm_limit(client: Client, cust_msg: Message):
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    # Tidak perlu lagi try-except untuk import
    # from ProjectMan.helpers.SQL.globals import addgvar # Sudah diimpor di atas

    input_str = get_arg(cust_msg) # Gunakan get_arg untuk mendapatkan argumen dengan lebih bersih
    
    if not input_str:
        return await cust_msg.edit("**Harap masukan angka untuk PM_LIMIT.**")
    
    Man = await cust_msg.edit("`Processing...`")
    
    if not input_str.isnumeric():
        return await Man.edit("**Harap masukan angka untuk PM_LIMIT.**")
    
    addgvar("PM_LIMIT", input_str) # Menggunakan fungsi addgvar yang sudah dimigrasi
    await Man.edit(f"**Set PM limit to** `{input_str}`")


@Client.on_message(filters.command(["pmpermit", "pmguard"], cmd) & filters.me)
async def onoff_pmpermit(client: Client, message: Message):
    input_str = get_arg(message)
    if input_str == "off":
        h_type = False
    elif input_str == "on":
        h_type = True
    else:
        return await edit_or_reply(message, "**Gunakan: `.pmpermit on` atau `.pmpermit off`**")

    # gvarstatus akan mengembalikan string "true" / "false" atau None
    current_pmpermit_status = gvarstatus("PMPERMIT")
    PMPERMIT_IS_ON = (current_pmpermit_status != "false") # Dianggap aktif jika "true" atau None

    if PMPERMIT_IS_ON and h_type: # Sedang ON dan ingin set ON
        await edit_or_reply(message, "**PMPERMIT Sudah Diaktifkan**")
    elif not PMPERMIT_IS_ON and not h_type: # Sedang OFF dan ingin set OFF
        await edit_or_reply(message, "**PMPERMIT Sudah Dimatikan**")
    else: # Perubahan status
        addgvar("PMPERMIT", str(h_type).lower()) # Simpan sebagai "true" atau "false"
        if h_type:
            await edit_or_reply(message, "**PMPERMIT Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**PMPERMIT Berhasil Dimatikan**")


@Client.on_message(filters.command("setpmpermit", cmd) & filters.me)
async def setpmpermit(client: Client, cust_msg: Message):
    """Set your own Unapproved message"""
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    # Tidak perlu lagi try-except untuk import
    # import ProjectMan.helpers.SQL.globals as sql # Sudah diimpor di atas (addgvar, gvarstatus, delgvar)

    Man = await cust_msg.edit("`Processing...`")
    
    message = cust_msg.reply_to_message
    if not message or not (message.text or message.caption):
        return await Man.edit("**Mohon Reply Ke Pesan (yang berisi teks/caption)**")

    msg_to_set = message.text or message.caption
    
    # Hapus gvar "unapproved_msg" sebelum menambahkan yang baru jika sudah ada
    # gvarstatus mengembalikan string atau None.
    # delgvar hanya perlu dipanggil jika gvarstatus mengembalikan sesuatu (bukan None).
    if gvarstatus("unapproved_msg") is not None:
        delgvar("unapproved_msg") # Menggunakan fungsi delgvar yang diimpor

    addgvar("unapproved_msg", msg_to_set) # Menggunakan fungsi addgvar yang sudah dimigrasi
    await Man.edit("**Pesan Berhasil Disimpan Ke Room Chat**")


@Client.on_message(filters.command("getpmpermit", cmd) & filters.me)
async def get_pmermit(client: Client, cust_msg: Message):
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    # Tidak perlu lagi try-except untuk import
    # import ProjectMan.helpers.SQL.globals as sql # Sudah diimpor di atas (addgvar, gvarstatus, delgvar)

    Man = await cust_msg.edit("`Processing...`")
    custom_message = gvarstatus("unapproved_msg") # Menggunakan fungsi gvarstatus yang sudah dimigrasi

    if custom_message is not None:
        await Man.edit(f"**Pesan PMPERMIT Yang Sekarang:**\n\n{custom_message}")
    else:
        await Man.edit(
            "**Anda Belum Menyetel Pesan Costum PMPERMIT,**\n"
            f"**Masih Menggunakan Pesan PM Default:**\n\n`{DEF_UNAPPROVED_MSG}`" # Wrap default message in code block
        )


@Client.on_message(filters.command("resetpmpermit", cmd) & filters.me)
async def reset_pmpermit(client: Client, cust_msg: Message):
    # gvarstatus akan mengembalikan string "true" / "false" atau None
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    # Tidak perlu lagi try-except untuk import
    # import ProjectMan.helpers.SQL.globals as sql # Sudah diimpor di atas (addgvar, gvarstatus, delgvar)

    Man = await cust_msg.edit("`Processing...`")
    custom_message = gvarstatus("unapproved_msg") # Menggunakan fungsi gvarstatus yang sudah dimigrasi

    if custom_message is None:
        await Man.edit("**Pesan PMPERMIT Anda Sudah Default**")
    else:
        delgvar("unapproved_msg") # Menggunakan fungsi delgvar yang diimpor
        await Man.edit("**Berhasil Mengubah Pesan Custom PMPERMIT menjadi Default**")


add_command_help(
    "pmpermit",
    [
        [
            f"ok atau {cmd}setuju",
            "Menerima pesan seseorang dengan cara balas pesannya atau tag dan juga untuk dilakukan di pm",
        ],
        [
            f"tolak atau {cmd}nopm",
            "Menolak pesan seseorang dengan cara balas pesannya atau tag dan juga untuk dilakukan di pm",
        ],
        [
            "pmlimit <angka>",
            "Untuk mengcustom pesan limit auto block pesan",
        ],
        [
            "setpmpermit <balas ke pesan>",
            "Untuk mengcustom pesan PMPERMIT untuk orang yang pesannya belum diterima.",
        ],
        [
            "getpmpermit",
            "Untuk melihat pesan PMPERMIT.",
        ],
        [
            "resetpmpermit",
            "Untuk Mereset Pesan PMPERMIT menjadi DEFAULT",
        ],
        [
            "pmpermit on/off",
            "Untuk mengaktifkan atau menonaktifkan PMPERMIT",
        ],
    ],
)
