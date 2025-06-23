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
        if part.type == "function_call":
            if part.name == "ask_database":
                counter = 0
                while part.type=="function_call":
                    counter +=1
                    query = json.loads(part.arguments)["query"]
                    print(query)
                    result_temp = sql_tool.ask_database(query)
                    if len(str(result_temp))>2000:
                        result_temp = "hasil query terlalu banyak"
                    if counter == 4:
                        result_final = client.responses.create(
                            model=config.GENAI_MODEL,
                            input=prompt + "\n\nQuery:" + query + "\n\nHasil query" + str(result_temp) + "\n\nGunakan hasil query untuk menjawab pertanyaan user",
                            instructions=config.SYSTEM_INSTRUCTION,
                        )
                        part = result_final.output[0]
                    else:
                        result_final = client.responses.create(
                            model=config.GENAI_MODEL,
                            input=prompt + "\n\nQuery:" + query + "\n\nHasil query" + str(result_temp) + "\n\nGunakan hasil query untuk menjawab pertanyaan user. Hanya gunakan tools ask_database apabila hasil query kosong atau hasil query terlalu banyak, coba gunakan strategi lain seperti menggunakan operator 'like' daripada = secara langsung.",
                            instructions=config.SYSTEM_INSTRUCTION,
                            tools=[sql_tool.ask_database_function],
                        )
                        part = result_final.output[0]
                text = part.content[0].text
            elif part.name == "plot_bar_line_area_chart" or part.name == "plot_pie_chart":
                args = json.loads(part.arguments)
                if part.name == "plot_bar_line_area_chart":
                    result_final = plot_tool.plot_bar_line_area_chart(args)
                else:
                    result_final = plot_tool.plot_pie_chart(args)
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
