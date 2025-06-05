import textwrap
import os
import pandas as pd
import numpy as np
import json
from openai import OpenAI

from utils import config

from . import memory, content_fetcher, tools

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_image_prompt(photo, text, context):
    image_base_64 = await content_fetcher.get_image_base64(photo, context)
    prompt = [
        {"mime_type": "image/jpeg", "data": image_base_64},
        text
    ]
    return prompt

async def main(update, context):
    if update.message.photo:
        prompt = await get_image_prompt(update.message.photo[-1], update.message.caption, context)
    elif update.message.reply_to_message:
        try:
            prompt = await get_image_prompt(update.message.reply_to_message.photo[-1], update.message.text, context)
        except:
            prompt = memory.get_chat_history(str(update.message.chat.id))
    else:
        prompt = memory.get_chat_history(str(update.message.chat.id))
    result = client.responses.create(
        model=config.GENAI_MODEL,
        input=prompt,
        tools=tools.tools,
    )
    print(result)
    for part in result.output:
        if part.type=="function_call":
            result_final = tools.ask_database(**json.loads(part.arguments))
        else:
            result_final = part.content[0].text.replace(f"{config.BOT_NAME.title()}: ", "").replace(f"{config.BOT_NAME.lower()}: ", "")
        if isinstance(result_final, pd.DataFrame):
            result_final = result_final.to_string()
        elif isinstance(result_final,np.float64) or isinstance(result_final, int):
            result_final = str(result_final)
        if ".png" in result_final:
            file_loc = "exports/charts/temp_chart.png"
            await context.bot.send_photo(
                chat_id=update.message.chat.id,
                photo=open(file_loc, "rb"),
            )
            memory.store_message(chatroom_id=str(update.message.chat_id), message=f"{config.BOT_NAME}: berikut adalah plotnya")
        else:
            for response_part in textwrap.wrap(result_final, 1999, expand_tabs=False, replace_whitespace=False, drop_whitespace=False,):
                memory.store_message(chatroom_id=str(update.message.chat.id), message=f"{config.BOT_NAME}: {response_part}")
                await context.bot.send_message(chat_id=update.message.chat.id, text=response_part)
    return
