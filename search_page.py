from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

search_page = Blueprint('search_page', __name__)

@search_page.route('/', methods=['GET', 'POST'])
def song_search():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                user_search = request.form.get('search_query')

                # I used ILIKE for case insensitive text based matching
                query = """
                    SELECT s_songname, s_albumid, s_genre, duration
                    FROM song
                    WHERE s_songname ILIKE %s
                """
                # applying % to beginning and end to make user error
                # more forgiving in case of typos and to easier
                # search functionality
                cur.execute(query, (f"%{user_search}%",))
                songs = cur.fetchall()

                # In case no songs match the user's search
                if not songs:
                    message = "No songs found matching your search."
                    return render_template('search.html', error=message)

        except psycopg2.DatabaseError as e:
            message = f"Database error: {str(e)}"
            return render_template('search.html', error=message)

        except Exception as e:
            message = f'Error when handling request: {str(e)}'
            return render_template('search.html', error=message)

        return render_template('search.html', songs=songs)

    return render_template('search.html') 
