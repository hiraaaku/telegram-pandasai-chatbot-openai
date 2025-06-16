import re
import traceback

from utils import logger, config
from services.chatbot import memory, chatbot, regex


async def route(update, context):
    username = str(update.message.from_user.first_name)
    if str(update.message.from_user.last_name).lower() != "none":
        username += " " + str(update.message.from_user.last_name)
    user_message = str(update.message.text)
    if update.message.photo:
        user_message = "*mengirim gambar*"
        if str(update.message.caption) != "None":
            user_message += " " + str(update.message.caption)
    if update.message.reply_to_message:
        if update.message.reply_to_message.text:
            user_message += f" (mereply ke ''{update.message.reply_to_message.text}'')" 
    memory.store_message(chatroom_id=str(update.message.chat.id), message=f"{username}: {user_message}")
    logger.message_print(update.message)
    engage_chatbot = re.search(regex.get_regex(), user_message.lower())
    engage_chatbot = True
    if user_message.lower() == f"{config.BOT_NAME} reset":
        del memory.chat_histories[str(update.message.chat.id)]
        await context.bot.send_message(chat_id=update.message.chat.id, text="history berhasil direset")
        return
    if engage_chatbot:
        try:
            await chatbot.main(update, context)
        except Exception as e:
            traceback.print_exc()
            result = get_serializable_dict(e.__dict__)
            await context.bot.send_message(chat_id=update.message.chat.id, text=str(result))
            return


def get_serializable_dict(json_obj):
    import json

    serializable_dict = {}
    for key, value in json_obj.items():
        try:
            json.dumps(value)
            serializable_dict[key] = value
        except Exception:
            pass
    return serializable_dict
