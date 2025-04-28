import psycopg2
import psycopg2.extras

def get_db_connection():
    conn = psycopg2.connect(
        host='localhost',
        database='music_app',
        user='postgres',
        password='0411BPTp',
        port='5432',
        cursor_factory=psycopg2.extras.DictCursor
    )
    return conn
