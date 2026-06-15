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
        port=int(os.getenv("DB_PORT")), # converte para o tipo int pq o que vem do .env é string
        cursorclass=pymysql.cursors.DictCursor #faz o cursor retornar os resultados como dicionario ao inves de duplas
    )