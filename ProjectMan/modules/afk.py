import time

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from config import CMD_HANDLER as cmd, BOTLOG_CHATID
from ProjectMan.helpers.msg_types import Types, get_message_type
from ProjectMan.helpers.parser import escape_markdown, mention_markdown
from ProjectMan.helpers.SQL.afk_db import get_afk, set_afk
from ProjectMan.modules.help import add_command_help
from ProjectMan.helpers.SQL.__init__ import LOGGER # Explicitly import LOGGER

MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 3


@Client.on_message(filters.me & filters.command("afk", cmd))
async def afk(client: Client, message: Message):
    if len(message.text.split()) >= 2:
        reason = message.text.split(None, 1)[1]
        set_afk(True, reason)
        await message.edit(
            "❏ {} **Telah AFK!**\n└ **Karena:** `{}`".format(
                mention_markdown(message.from_user.id, message.from_user.first_name),
                escape_markdown(reason),
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

    get = get_afk()
    if get and get["afk"]:
        cid_int = message.chat.id
        cid_str = str(message.chat.id).replace("-100", "")

        if cid_int in AFK_RESTIRECT:
            if int(AFK_RESTIRECT[cid_int]) >= int(time.time()):
                return
        AFK_RESTIRECT[cid_int] = int(time.time()) + DELAY_TIME

        reason = get["reason"] if get["reason"] else "Alasan tidak diberikan."

        if reason:
            await message.reply(
                "❏ {} **Sedang AFK!**\n└ **Karena:** `{}`".format(
                    client.me.mention, escape_markdown(reason)
                )
            )
        else:
            await message.reply(
                f"**Maaf** {client.me.first_name} **Sedang AFK!**"
            )

        message_content = ""
        if message.text:
            message_content = message.text
        elif message.caption:
            message_content = message.caption
        elif get_message_type(message)[1] != Types.TEXT:
            message_content = get_message_type(message)[1].name

        # Handle message.chat.title potentially being None for private chats
        chat_title_for_log = message.chat.title if message.chat.title else "Private Chat"
        
        MENTIONED.append(
            {
                "user": message.from_user.first_name,
                "user_id": message.from_user.id,
                "chat": chat_title_for_log, # Use the handled chat title
                "chat_id": cid_str,
                "text": message_content,
                "message_id": message.id,
            }
        )
        try:
            if BOTLOG_CHATID:
                await client.send_message(
                    BOTLOG_CHATID,
                    "**#MENTION**\n • **Dari :** {}\n • **Grup :** `{}`\n • **Pesan :** `{}`".format(
                        message.from_user.mention,
                        escape_markdown(chat_title_for_log),
                        escape_markdown(message_content[:3500]),
                    ),
                )
        except Exception as e:
            LOGGER(__name__).error(f"Gagal mengirim log mention ke BOTLOG_CHATID: {e}")


@Client.on_message(filters.me & filters.group, group=12)
async def no_longer_afk(client: Client, message: Message):
    global MENTIONED
    global AFK_RESTIRECT

    get = get_afk()
    if get and get["afk"]:
        set_afk(False, "")
        try:
            if BOTLOG_CHATID:
                await client.send_message(BOTLOG_CHATID, "**Anda sudah tidak lagi AFK!**")
        except Exception as e:
            LOGGER(__name__).error(f"Gagal mengirim pesan tidak AFK ke BOTLOG_CHATID: {e}")
            pass

        if MENTIONED:
            text = "**Total {} Mention Saat Sedang AFK**\n".format(len(MENTIONED))
            for x in MENTIONED:
                msg_text_display = x["text"]
                if len(msg_text_display) >= 11:
                    msg_text_display = "{}...".format(msg_text_display[:500])

                text += "- [{}](https://t.me/c/{}/{}) ({}): `{}`\n".format(
                    escape_markdown(x["user"]),
                    x["chat_id"],
                    x["message_id"],
                    escape_markdown(x["chat"]),
                    escape_markdown(msg_text_display),
                )
            try:
                if BOTLOG_CHATID:
                    await client.send_message(BOTLOG_CHATID, text)
            except Exception as e:
                LOGGER(__name__).error(f"Gagal mengirim ringkasan mention AFK ke BOTLOG_CHATID: {e}")
                pass
        MENTIONED = []
        AFK_RESTIRECT = {}

add_command_help(
    "afk",
    [
        [
            "afk <alasan>",
            "Memberi tahu orang yang menandai atau membalas salah satu pesan atau dm Anda kalau Anda sedang AFK.",
        ],
    ],
)
