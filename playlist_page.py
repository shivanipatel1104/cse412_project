from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

playlist_page = Blueprint('playlist_page', __name__)


@playlist_page.route('/', methods=['GET'])
def playlist_info():
    playlist_id = session.get('playlist_id')
    user_id = session.get('user_id')
    is_followed = False

    song_played_message = session.get('song_played_message')
    song_liked_message = session.get('song_liked_message')

    if not playlist_id:
        return render_template('playlist.html', error="Error with session playlist id")

    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT p_playlistname FROM playlist WHERE p_playlistID = %s", (playlist_id,))
            row = cur.fetchone()
            playlist_name = row[0] if row else "Untitled Playlist"

            query = """
                SELECT s_songID, s_songname, al_albumName, a_artistName, s_genre, duration
                FROM playlistsongs
                JOIN playlist ON p_playlistID = ps_playlistID
                JOIN song ON s_songID = ps_songID
                JOIN album ON al_albumID = s_albumID
                JOIN artist ON a_artistID = al_artistID
                WHERE p_playlistID = %s
            """
            cur.execute(query, (playlist_id,))
            songs = cur.fetchall()

            check_followed = """
                SELECT EXISTS (
                    SELECT 1
                    FROM playlist_followers
                    WHERE pf_playlistID = %s AND pf_userID = %s
                )
            """
            cur.execute(check_followed, (playlist_id, user_id))
            result = cur.fetchone()
            is_followed = result[0]

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

    finally:
        conn.close()

    return render_template('playlist.html', songs=songs, is_followed=is_followed, playlist_name=playlist_name, song_played_message=song_played_message, song_liked_message=song_liked_message)


@playlist_page.route('/delete_song', methods=['POST'])
def delete_playlist_song():
    try:
        playlist_id = session.get('playlist_id')
        song_id = request.form.get('song_delete')

        if not song_id or not playlist_id:
            return render_template('playlist.html', error='Error with song id or playlist id session')

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                query = """
                    DELETE FROM playlistsongs
                    WHERE ps_playlistID = %s AND ps_songID = %s
                """
                cur.execute(query, (playlist_id, song_id))
                message = "Song was successfully removed from playlist!"

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

    return redirect(url_for('playlist_page.playlist_info'))


@playlist_page.route('/follow_playlist', methods=['POST'])
def follow_or_unfollow_playlist():
    try:
        playlist_id = session.get('playlist_id')
        user_id = session.get('user_id')

        if not playlist_id or not user_id:
            return render_template('playlist.html', error='Error with user id or playlist id sessions')

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                query = """
                    SELECT pf_playlistID
                    FROM playlist_followers
                    WHERE pf_userID = %s AND pf_playlistID = %s
                """
                cur.execute(query, (user_id, playlist_id))
                is_followed = cur.fetchone()

                if is_followed:
                  
                    remove_follow = """
                        DELETE FROM playlist_followers
                        WHERE pf_playlistID = %s AND pf_userID = %s
                    """
                    cur.execute(remove_follow, (playlist_id, user_id))
                    message = 'Playlist successfully removed from your follow list'
                else:

                    add_follow = """
                        INSERT INTO playlist_followers (pf_playlistID, pf_userID)
                        VALUES (%s, %s)
                    """
                    cur.execute(add_follow, (playlist_id, user_id))
                    message = 'Playlist successfully added to your follow list!'

                return redirect(url_for('playlist_page.playlist_info'))

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

@playlist_page.route('/play', methods=['POST'])
def song_play_handler():
    try:
        song_id = request.form.get('song_id')

        if not song_id:
            return render_template('playlist.html', error='Error retrieving song id')

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE song
                    SET s_times_played = s_times_played + 1
                    WHERE s_songID = %s
                """
                cur.execute(query, (song_id,)) 

                query = 'SELECT s_songname, s_times_played FROM song WHERE s_songID = %s'
                cur.execute(query, (song_id,))

                result = cur.fetchone()
                song_name = result[0]
                times_played = result[1]

        session['song_played_message'] = f'{song_name} was successfully played! You have played this song {times_played} times!'

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

    return redirect(url_for('playlist_page.playlist_info'))


@playlist_page.route('/like', methods = ['POST'])
def like_song_handler():
    try:
        song_id = request.form.get('like_song')
        user_id = session.get('user_id')

        if not song_id:
            return render_template('playlist.html', error="Error: No song session id")

        if not user_id:
            return render_template('playlist.html', error="Error: No user session id")

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
               
                song_name_query = 'SELECT s_songname FROM song WHERE s_songID = %s'
                cur.execute(song_name_query, (song_id,))
                result = cur.fetchone()

                if result:
                    song_name = result[0]

                else:
                    mess = 'Error: song id does not exist'
                    return render_template('playlist.html', error=mess)

                
                query = """
                    SELECT *
                    FROM likedsongs
                    WHERE l_userID = %s AND l_songID = %s
                """
                cur.execute(query, (user_id, song_id))
                is_liked = cur.fetchone()

                
                if is_liked:
                    message = f"{song_name} removed from liked songs!"
                    query = """
                        DELETE FROM likedsongs
                        WHERE l_userID = %s AND l_songID = %s 
                    """
                    cur.execute(query, (user_id, song_id))

                
                else:
                    message = f"{song_name} added to liked songs!"
                    query = """
                        INSERT INTO likedsongs (l_userID, l_songID)
                        VALUES (%s, %s)
                    """
                    cur.execute(query, (user_id, song_id))
                

                song_data_query = """
                    SELECT s_songname
                    FROM song
                    WHERE s_songID = %s
                """
                cur.execute(song_data_query, (song_id,))

                result = cur.fetchone()

                if result:
                    song_name = result[0]

                else:
                    return render_template('playlist.html', error='Unknown song name')
                
                session['song_liked_message'] = message

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

    return redirect(url_for('playlist_page.playlist_info'))
