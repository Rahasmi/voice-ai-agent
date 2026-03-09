import psycopg2

conn = psycopg2.connect(
    database="appointments_db",
    user="postgres",
    password="1234",
    host="localhost"
)