import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='music_app',
        user='postgres',
        password='1104',
        port='5432',
    )
    return conn
