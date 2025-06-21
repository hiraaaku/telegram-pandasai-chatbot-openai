import textwrap
import os
import json
from openai import OpenAI

from utils import config

from . import memory, content_fetcher
from .tools import tool_collection, sql_tool, plot_tool

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
        instructions=config.SYSTEM_INSTRUCTION,
        tools=tool_collection.tools,
    )
    for part in result.output:
        print(part)
        if part.type=="function_call":
            if part.name == "ask_database":
                query = json.loads(part.arguments)["query"]
                print(query)
                result_final = sql_tool.ask_database(query)
            # elif ".png" in str(result_final):
                result = client.responses.create(
                    model=config.GENAI_MODEL,
                    input=prompt + "\n\nQuery:" + query + "\n\nHasil query" + str(result_final) + "\n\nGunakan jawaban dari PandasAI untuk menjawab permintaan user",
                    instructions=config.SYSTEM_INSTRUCTION,
                )
                text=result.output[0].content[0].text
            elif part.name == "plot_bar_line_area_chart":
                args = json.loads(part.arguments)
                result_final = plot_tool.plot_bar_line_area_chart(args)
                if result_final == "success":
                    file_loc = "temp_chart.jpg"
                    await context.bot.send_photo(
                        chat_id=update.message.chat.id,
                        photo=open(file_loc, "rb"),
                    )
                    memory.store_message(chatroom_id=str(update.message.chat_id), message=f"{config.BOT_NAME}: berikut adalah plotnya")
                    return
                else:
                    text = result_final
        else:
            text = part.content[0].text
        text = text.replace(f"{config.BOT_NAME.lower()}: ", "").replace(f"{config.BOT_NAME.lower()}: ", "")
        for response_part in textwrap.wrap(text, 1999, expand_tabs=False, replace_whitespace=False, drop_whitespace=False,):
            memory.store_message(chatroom_id=str(update.message.chat.id), message=f"{config.BOT_NAME}: {response_part}")
            await context.bot.send_message(chat_id=update.message.chat.id, text=response_part)
    return
