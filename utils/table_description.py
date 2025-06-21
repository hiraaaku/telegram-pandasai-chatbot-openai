import os
from dotenv import load_dotenv

from .sql_connector import get_mysql_connection

load_dotenv()

table_names = os.getenv("DB_TABLE").split(",")

def get_table_description():
    table_description = ""
    conn = get_mysql_connection()
    for table in table_names:
        table_description += (f"Nama tabel: {table}\n")
        query = f"describe {table}"
        try:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
            for field in result:
                table_description += field["Field"] + " " + field["Type"] + "\n"
        except Exception as e:
            print(str(e))
        table_description += "\n"
    if len(table_description) >=10:
        return table_description
    else:
        return "failed to get table_description"

table_description = get_table_description()
