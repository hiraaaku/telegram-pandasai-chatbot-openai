import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pandasai.llm import OpenAI
from pandasai import SmartDatalake, SmartDataframe
from pandasai.connectors import MySQLConnector
from dotenv import load_dotenv

load_dotenv()

timeout=int(os.environ.get('DB_TIMEOUT'))
openai_llm = OpenAI(
    api_token=os.environ.get("OPENAI_API_KEY"),
)

def get_tables(table_names):
    tables = []
    for table_name in table_names:
        mysql_connector = MySQLConnector(
            config={
                "host": os.environ.get("DB_HOST"),
                "port": os.environ.get("DB_PORT"),
                "database": os.environ.get("DB_NAME"),
                "username": os.environ.get("DB_USERNAME"),
                "password": os.environ.get("DB_PASSWORD"),
                "allow_public_key_retrieval": True,
                "table": table_name,
            }
        )
        sdf = SmartDataframe(mysql_connector)
        tables.append(sdf)
    return tables

table_names = os.environ.get("DB_TABLE").split(",")  
tables = get_tables(table_names)
lake = SmartDatalake(
    tables,
    config={"llm": openai_llm}
)

def ask_database(question):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(lake.chat, str(question))
        try:
            result = future.result(timeout=timeout)
            print(question)
            print(result)
            print(lake.last_code_generated)
            return result
        except TimeoutError:
            return "⏱️ Query took too long and was stopped."

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

