import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_mysql_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
