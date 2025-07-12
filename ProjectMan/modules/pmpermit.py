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

from config import CMD_HANDLER as cmd
from ProjectMan import TEMP_SETTINGS
from ProjectMan.helpers.adminHelpers import DEVS
from ProjectMan.helpers.basic import edit_or_reply
from ProjectMan.helpers.SQL.globals import addgvar, gvarstatus, delgvar
from ProjectMan.helpers.SQL.pm_permit_sql import is_approved, approve, dissprove
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
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return

    if await auto_accept(client, message) or message.from_user.is_self:
        message.continue_propagation()
        return

    if message.chat.id != 777000:
        pm_limit_str = gvarstatus("PM_LIMIT")
        PM_LIMIT = int(pm_limit_str) if pm_limit_str and pm_limit_str.isnumeric() else 5

        getmsg = gvarstatus("unapproved_msg")
        UNAPPROVED_MSG = getmsg if getmsg is not None else DEF_UNAPPROVED_MSG

        apprv = is_approved(message.chat.id)
        if not apprv and message.text != UNAPPROVED_MSG:
            if message.chat.id not in TEMP_SETTINGS:
                TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ""
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] = 0

            if TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] != message.text:
                async for prev_bot_msg in client.search_messages(
                    message.chat.id,
                    from_user="me",
                    limit=10,
                    query=UNAPPROVED_MSG,
                ):
                    try:
                        await prev_bot_msg.delete()
                    except Exception:
                        pass

                if TEMP_SETTINGS["PM_COUNT"][message.chat.id] < (int(PM_LIMIT) - 1):
                    ret = await message.reply_text(UNAPPROVED_MSG)
                    if ret:
                        TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ret.text
                
                TEMP_SETTINGS["PM_COUNT"][message.chat.id] += 1
            
            if TEMP_SETTINGS["PM_COUNT"][message.chat.id] >= PM_LIMIT:
                await message.reply("**Maaf anda Telah Di Blokir Karna Spam Chat**")
                try:
                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except Exception:
                    pass

                await client.block_user(message.chat.id)

    message.continue_propagation()


async def auto_accept(client: Client, message: Message):
    if message.chat.id in DEVS:
        try:
            approve(message.chat.id)
            await client.send_message(
                message.chat.id,
                f"<b>Menerima Pesan!!!</b>\n{message.from_user.mention} <b>Terdeteksi Developer PyroMan-Userbot</b>",
                parse_mode=enums.ParseMode.HTML,
            )
            return True
        except Exception as e:
            LOGGER(__name__).error(f"Error in auto_accept for DEVS: {e}")
            pass

    if message.chat.id not in [client.me.id, 777000]:
        if is_approved(message.chat.id):
            return True

        async for msg in client.get_chat_history(message.chat.id, limit=1):
            if msg.from_user.id == client.me.id:
                try:
                    if message.chat.id not in TEMP_SETTINGS:
                        TEMP_SETTINGS["PM_COUNT"][message.chat.id] = 0
                        TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id] = ""

                    del TEMP_SETTINGS["PM_COUNT"][message.chat.id]
                    del TEMP_SETTINGS["PM_LAST_MSG"][message.chat.id]
                except Exception:
                    pass

                try:
                    approve(message.chat.id)
                    async for unapproved_msg_del in client.search_messages(
                        message.chat.id,
                        from_user="me",
                        limit=10,
                        query=UNAPPROVED_MSG,
                    ):
                        try:
                            await unapproved_msg_del.delete()
                        except Exception:
                            pass
                    return True
                except Exception as e:
                    LOGGER(__name__).error(f"Error in auto_accept after userbot reply: {e}")
                    pass

    return False


@Client.on_message(
    filters.command(["ok", "setuju", "approve"], cmd) & filters.me & filters.private
)
async def approvepm(client: Client, message: Message):
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
        approve(uid)
        await message.edit(f"**Menerima Pesan Dari** [{name0}](tg://user?id={uid})!")
        if uid in TEMP_SETTINGS["PM_COUNT"]:
            del TEMP_SETTINGS["PM_COUNT"][uid]
        if uid in TEMP_SETTINGS["PM_LAST_MSG"]:
            del TEMP_SETTINGS["PM_LAST_MSG"][uid]
        async for unapproved_msg_del in client.search_messages(
            uid,
            from_user="me",
            limit=10,
            query=UNAPPROVED_MSG,
        ):
            try:
                await unapproved_msg_del.delete()
            except Exception:
                pass

    except Exception:
        await message.edit(
            f"[{name0}](tg://user?id={uid}) mungkin sudah disetujui untuk PM."
        )
        return


@Client.on_message(
    filters.command(["tolak", "nopm", "disapprove"], cmd) & filters.me & filters.private
)
async def disapprovepm(client: Client, message: Message):
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

    dissprove(uid)

    await message.edit(
        f"**Pesan** [{name0}](tg://user?id={uid}) **Telah Ditolak, Mohon Jangan Melakukan Spam Chat!**"
    )
    if uid in TEMP_SETTINGS["PM_COUNT"]:
        del TEMP_SETTINGS["PM_COUNT"][uid]
    if uid in TEMP_SETTINGS["PM_LAST_MSG"]:
        del TEMP_SETTINGS["PM_LAST_MSG"][uid]


@Client.on_message(filters.command("pmlimit", cmd) & filters.me)
async def setpm_limit(client: Client, cust_msg: Message):
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )

    input_str = get_arg(cust_msg)
   
    if not input_str:
        return await cust_msg.edit("**Harap masukan angka untuk PM_LIMIT.**")
    
    Man = await cust_msg.edit("`Processing...`")
    
    if not input_str.isnumeric():
        return await Man.edit("**Harap masukan angka untuk PM_LIMIT.**")
    
    addgvar("PM_LIMIT", input_str)
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

    current_pmpermit_status = gvarstatus("PMPERMIT")
    PMPERMIT_IS_ON = (current_pmpermit_status != "false")
    if PMPERMIT_IS_ON and h_type:
        await edit_or_reply(message, "**PMPERMIT Sudah Diaktifkan**")
    elif not PMPERMIT_IS_ON and not h_type:
        await edit_or_reply(message, "**PMPERMIT Sudah Dimatikan**")
    else:
        addgvar("PMPERMIT", str(h_type).lower())
        if h_type:
            await edit_or_reply(message, "**PMPERMIT Berhasil Diaktifkan**")
        else:
            await edit_or_reply(message, "**PMPERMIT Berhasil Dimatikan**")


@Client.on_message(filters.command("setpmpermit", cmd) & filters.me)
async def setpmpermit(client: Client, cust_msg: Message):
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )

    Man = await cust_msg.edit("`Processing...`")
    
    message = cust_msg.reply_to_message
    if not message or not (message.text or message.caption):
        return await Man.edit("**Mohon Reply Ke Pesan (yang berisi teks/caption)**")

    msg_to_set = message.text or message.caption
    
    if gvarstatus("unapproved_msg") is not None:
        delgvar("unapproved_msg")

    addgvar("unapproved_msg", msg_to_set)
    await Man.edit("**Pesan Berhasil Disimpan Ke Room Chat**")


@Client.on_message(filters.command("getpmpermit", cmd) & filters.me)
async def get_pmermit(client: Client, cust_msg: Message):
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    Man = await cust_msg.edit("`Processing...`")
    custom_message = gvarstatus("unapproved_msg")

    if custom_message is not None:
        await Man.edit(f"**Pesan PMPERMIT Yang Sekarang:**\n\n{custom_message}")
    else:
        await Man.edit(
            "**Anda Belum Menyetel Pesan Costum PMPERMIT,**\n"
            f"**Masih Menggunakan Pesan PM Default:**\n\n`{DEF_UNAPPROVED_MSG}`"
        )


@Client.on_message(filters.command("resetpmpermit", cmd) & filters.me)
async def reset_pmpermit(client: Client, cust_msg: Message):
    pmpermit_status = gvarstatus("PMPERMIT")
    if pmpermit_status == "false":
        return await cust_msg.edit(
            f"**Anda Harus Menyetel Var** `PMPERMIT` **Ke** `True`\n\n**Bila ingin Mengaktifkan PMPERMIT Silahkan Ketik:** `{cmd}pmpermit on`"
        )
    Man = await cust_msg.edit("`Processing...`")
    custom_message = gvarstatus("unapproved_msg")

    if custom_message is None:
        await Man.edit("**Pesan PMPERMIT Anda Sudah Default**")
    else:
        delgvar("unapproved_msg")
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
