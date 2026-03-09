import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

db = psycopg2.connect(
    host="localhost",
    database="clinic_ai",
    user="postgres",
    password="7730897312",
    port="5433"
)

cursor = db.cursor()