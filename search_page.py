from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

search_page = Blueprint('search_page', __name__)

# Shows results of searched song name with some pattern matching
@search_page.route('/', methods=['GET', 'POST'])
def song_search():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                user_search = request.form.get('search_query')

                # I used ILIKE for case insensitive text based matching
                query = """
                    SELECT s_songid, s_songname, al_albumName, a_artistName, s_genre, duration
                    FROM song 
					JOIN album ON s_albumID = al_albumID
                    JOIN artist ON al_artistID = a_artistID
                    WHERE s_songname ILIKE %s
                    LIMIT 20;
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

# Handle song selection functionality
@search_page.route('/', methods=['POST'])
def song_select_handler():
    try:
        song_id = request.form.get("song_select")

        if not song_id:
            raise Exception("Invalid song selected")

        session['song_id'] = song_id
        return redirect(url_for('song_page.song_info'))

    except Exception as e:
        mess = f'Error when handling request: {str(e)}'
        return render_template('search.html', error=mess)

# Handle adding song to playlist
@search_page.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    try:
        song_id = request.form.get('song_id')

        if not song_id:
            return render_template('search.html', error='Error when trying to obtain song id')

        print(f"SONG ID FOR CHOSEN SONG: {song_id}")
        session['song_id'] = song_id

    except Exception as e:
        mess = f'Error when handling request: {str(e)}'
        return render_template('search.html', error=mess)

    return redirect(url_for('playlist_select_page.show_playlists'))