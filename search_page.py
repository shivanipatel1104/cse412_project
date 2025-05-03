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

              
                query = """
                    SELECT s_songID, s_songname, al_albumName, a_artistName, s_genre, duration
                    FROM song 
					JOIN album ON s_albumID = al_albumID
                    JOIN artist ON al_artistID = a_artistID
                    WHERE s_songname ILIKE %s
                    LIMIT 20;
                """
               
                cur.execute(query, (f"%{user_search}%",))
                songs = cur.fetchall()

                
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
    
@search_page.route('/add_liked_song', methods=['POST'])
def add_liked_song():
    try:
        song_id = request.form.get("song_select")
        user_id = session.get('user_id')

        if not song_id or not user_id:
            return render_template('search.html', error='Missing song or user ID')

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                query = """
                    SELECT *
                    FROM likedsongs
                    WHERE l_userID = %s AND l_songID = %s
                """
                cur.execute(query, (user_id, song_id))
                already_liked = cur.fetchone()

                if already_liked:
                    message = 'Song already in your liked songs!'
                else:
                    insert_query = """
                        INSERT INTO likedsongs (l_userID, l_songID)
                        VALUES (%s, %s)
                    """
                    cur.execute(insert_query, (user_id, song_id))
                    message = 'Song successfully added to your liked songs!'

                return render_template('search.html', message=message)
            
    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('search.html', error=message)

    except Exception as e:
        message = f'Unexpected error: {str(e)}'
        return render_template('search.html', error=message)

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