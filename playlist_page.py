from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

playlist_page = Blueprint('playlist_page', __name__)

# Show songs in user playlist. Also is_followed functionality:
# If user follows playlist, then set if_followed to true, else false
# if_followed is for changing status of 'followed button'. I.E. the 'followed button' text
# could be 'followed' if is_followed is true and 'unfollowed' if is_followed is false
@playlist_page.route('/', methods=['GET'])
def playlist_info():
    playlist_id = session.get('playlist_id')
    user_id = session.get('user_id')
    is_followed = False # default to false, will query later

    if not playlist_id:
        return render_template('playlist.html', error="Error with session playlist id")

    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            # Show song name, album name, and artist name for
            # each song in the playlist (IDed by playlist_id)
            query = """
                SELECT s_songname, al_albumName, a_artistName
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

            # If user follows playlist
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

    return render_template('playlist.html', songs=songs, is_followed=is_followed)

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

                return render_template('playlist.html', message=message)

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)

# Allow user to follow playlist or unfollow if they already are following
@playlist_page.route('follow_playlist', methods=['POST'])
    try:
        playlist_id = session.get('playlist_id')
        user_id = session.get('user_id')

        if not playlist_id or not user_id:
            return render_template('playlist.html', error='Error with user id or playlist id sessions')

        conn = get_db_connection()
        with conn:
            with con.cursor() as cur:
                query = """
                    SELECT pf_playlistID
                    FROM playlist_followers
                    WHERE pf_userID = %s
                """
                cur.execute(query, (user_id,))
                is_followed = cur.fetchone()

                if is_followed:
                    # remove from followed
                    remove_follow = """
                        DELETE FROM playlist_followers
                        WHERE pf_playlistID = %s AND pf_userID = %s
                    """
                    cur.execute(remove_follow, (playlist_id, user_id))
                    message = 'Playlist successfully removed from your follow list'
                else:
                    # add to followed
                    add_follow = """
                        INSERT INTO playlist_followers (pf_playlistID, pf_userID)
                        VALUES (%s, %s)
                    """
                    cur.execute(add_follow, (playlist_id, user_id))
                    message = 'Playlist successfully added to your follow list!'

                return render_template('playlist.html', message=message)

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist.html', error=message)






