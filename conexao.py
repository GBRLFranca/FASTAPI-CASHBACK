import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

def connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT")), 
        init_command="SET time_zone = '-03:00'",
        cursorclass=pymysql.cursors.DictCursor 
    )