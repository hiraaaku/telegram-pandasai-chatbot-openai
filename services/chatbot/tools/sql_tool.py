from dotenv import load_dotenv
from utils.sql_connector import get_mysql_connection
from utils.table_description import table_description

load_dotenv()


def ask_database(query):
    if not any(word in query.lower() for word in ["delete", "remove"]):
        try:
            conn = get_mysql_connection()
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            conn.close()
            print(result)
            if len(result)<1:
                return "query return empty list"
            return result
        except Exception as e:
            return str(e)

ask_database_function = {
     "type": "function",
     "name": "ask_database",
    "description": f"Gunakan fungsi ini jika user bertanya tentang pertanyaan yang berhubungan data yang ada pada database, kamu sudah memiliki akses penuh pada database ini, berikut informasi mengenai tabel yang tersedia:\n\n{table_description}",
     "parameters": {
         "type": "object",
         "properties": {
             "query": {
                 "type": "string",
                 "description": "query untuk mengambil data",
             },
         },
         "required": ["query"],
     },
}
