from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

song_page = Blueprint('song_page', __name__)

@song_page.route('/', methods=['GET'])
def song_info():
    user_id = session.get('user_id')
    song_id = session.get('song_id')

    if not song_id or not user_id:
        mess = f'Error: No session song id'
        return render_template('song.html', error=mess)

    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            song_data_query = """
                SELECT s_songname, s_genre, s_duration
                FROM song
                WHERE s_songID = %s
            """

            cur.execute(song_data_query, (song_id,))
            song_data = cur.fetchone()

            if not song_data:
                return render_template('song.html', error='Song not found')

            check_liked = """
                SELECT EXISTS (
                    SELECT 1
                    FROM liked_songs
                    WHERE l_userID = %s AND l_songID = %s
                )
            """
            cur.execute(check_liked, (user_id, song_id))
            result = cur.fetchone()
            is_liked = result[0]

    except psycopg2.DatabaseError as e:
        mess = f"Database error: {str(e)}"
        return render_template('song.html', error=mess)

    except Exception as e:
        mess = f'Error when handling request: {str(e)}'
        return render_template('song.html', error=mess)

    return render_template('song.html', song_data=song_data, is_liked=is_liked)


@song_page.route('/play', methods=['POST'])
def song_play_handler():
    try:
        play_clicked = request.form.get("play_button_clicked")

        if play_clicked:
            song_id = session.get('song_id')

            if not song_id:
                mess = f'Error: No session song id'
                return render_template('song.html', error=mess)

            conn = get_db_connection()
            with conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE song
                        SET s_times_played = s_times_played + 1
                        WHERE s_songID = %s
                    """
                    cur.execute(query, (song_id,))

                    return render_template('song.html', played_message='Song Successfully Played!')

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist_list.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)

@song_page.route('/like', methods=['POST'])
def song_like_handler():
    try:
        like_clicked = request.form.get('like_button_clicked')

        if like_clicked:
            song_id = session.get('song_id')
            user_id = session.get('user_id')

            if not song_id:
                return render_template('song.html', error="Error: No song session id")

            if not user_id:
                return render_template('song.html', error="Error: No user session id")

            conn = get_db_connection()
            with conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT *
                        FROM likedsongs
                        WHERE l_userID = %s AND l_songID = %s
                    """
                    cur.execute(query, (user_id, song_id))
                    is_liked = cur.fetchone()

                    if is_liked:
                        message = "Song removed from liked songs!"
                        query = """
                            DELETE FROM liked_songs
                            WHERE l_userID = %s AND l_songID = %s 
                        """
                    
                    else:
                        message = "Song added to liked songs!"
                        query = """
                            INSERT INTO likedsongs (l_userID, l_songID)
                            VALUES (%s, %s)
                        """
                    cur.execute(query, (user_id, song_id))

                    
                    song_data_query = """
                        SELECT s_songname, s_genre, s_duration
                        FROM song
                        WHERE s_songID = %s
                    """
                    cur.execute(song_data_query, (song_id,))
                    song_data = cur.fetchone()

                    return render_template('song.html', message=message, song_data=song_data)

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist_list.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)
