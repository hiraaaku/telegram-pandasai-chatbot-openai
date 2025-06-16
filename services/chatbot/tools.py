import os
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
import pandas as pd

openai_llm = OpenAI(
    api_token=os.environ.get("OPENAI_API_KEY"),
)

def ask_database(question):
    df = pd.read_csv("data_source.csv")
    sdf = SmartDataframe(df, config={"llm": openai_llm, "use_duckdb":True})
    result = sdf.chat(str(question))
    print(question)
    print(result)
    print(sdf.last_code_generated)
    return result

# Define the function declaration for the model
ask_database_function = {
     "type": "function",
     "name": "ask_database",
     "description": "Gunakan fungsi ini jika user bertanya tentang pertanyaan atau membuat plot yang berhubungan tentang data yang ada pada database, kamu sudah memiliki akses penuh pada database ini. Pastikan jawaban yang dihasilkan oleh pandasAI ini tidak mengandung bilangan saintifik",
     "parameters": {
         "type": "object",
         "properties": {
             "question": {
                 "type": "string",
                 "description": "Pertanyaan yang dapat dimengerti PandasAI",
             },
         },
         "required": ["question"],
     },
}

# Configure the client and tools
tools = [ask_database_function]

