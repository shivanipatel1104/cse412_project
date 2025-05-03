from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2
from enum import Enum
from datetime import datetime


class PlaylistType(Enum):
    TOP10_LIST = 'top10_list' 
    USER_LIST = 'user_list'
    CREATE_PLAYLIST = 'create_playlist' 

playlist_list_page = Blueprint('playlist_list_page', __name__)

@playlist_list_page.route('/', methods=['GET', 'POST'])
def user_playlists():
    
    playlists = []
    button_type = PlaylistType.USER_LIST 

   
    curr_user_id = session['user_id']
    if not curr_user_id:
        return render_template('playlist_list.html', error='User session credentials are not authorized')
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            button_string = request.form.get("button_click") 

            if button_string:
                try:
                    button_type = PlaylistType(button_string)
                except ValueError:
                    button_type = PlaylistType.USER_LIST 

      
            if button_type == PlaylistType.CREATE_PLAYLIST:
                playlist_name = request.form.get("playlist_name")
                author_id = session.get('user_id') 
                time_created = datetime.now()

                if not playlist_name:
                    return render_template('playlist_list.handling', error="Playlist name required")

                playlist_query = """
                    INSERT INTO playlist (p_playlistname, p_author_userid, p_timecreated)
                    VALUES (%s, %s, %s)
                """
                get_playlist_id_query = """
                    SELECT p_playlistid
                    FROM playlist
                    WHERE p_playlistname = %s AND p_author_userid = %s
                """
                playlist_follower_query = """
                    INSERT INTO playlist_followers (pf_playlistid, pf_userid)
                    VALUES (%s, %s)
                """


                cur.execute(playlist_query, (playlist_name, author_id, time_created))
                conn.commit()

                cur.execute(get_playlist_id_query, (playlist_name, author_id))
                playlist_id_data = cur.fetchone()

                playlist_id = playlist_id_data[0]

                cur.execute(playlist_follower_query, (playlist_id, author_id))
                conn.commit()

            if button_type == PlaylistType.TOP10_LIST:
                query = """
                    -- Show top n most followed playlists
                    SELECT p_playlistID, 
                           COUNT(pf_playlistID) AS num_follows, 
                           p_playlistname, 
                           u_username -- username for author of playlist
                    FROM playlist
                    JOIN users ON p_author_userid = u_userID
                    JOIN playlist_followers ON pf_playlistID = p_playlistID
                    GROUP BY p_playlistID, p_playlistname, u_username
                    ORDER BY num_follows DESC -- descending to get the most followed playlists first
                    LIMIT 10; -- replace 10 with the number of top playlists to show
                """

                cur.execute(query)
                playlists = cur.fetchall()
            else: 
                query = """
                    -- Select all playlists a user is following (show playlist name and playlist author name)
                    SELECT p_playlistID, p_playlistname, u_username -- username for author of playlist
                    FROM playlist
                    JOIN playlist_followers ON pf_playlistID = p_playlistID -- to access playlist name
                    JOIN users ON p_author_userid = u_userID -- to access username of playlist author
                    WHERE pf_userID = %s; -- to access playlists for current user
                """
                cur.execute(query, (curr_user_id,))
                playlists = cur.fetchall()

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist_list.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)

   
    return render_template('playlist_list.html', playlists=playlists, button_type=button_type)


@playlist_list_page.route('/select_playlist', methods=['POST'])
def playlist_select_handler():
    try:
        playlist_id = request.form.get("playlist_select")

        if not playlist_id:
            raise Exception("Invalid playlist selected")

        session['playlist_id'] = playlist_id
        return redirect(url_for('playlist_page.playlist_info'))        

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)


@playlist_list_page.route('/delete_playlist', methods=['POST'])
def delete_playlist():
    try:
        playlist_id = request.form.get("playlist_select")
        curr_user_id = session.get('user_id')

        if not playlist_id:
            return render_template('playlist_list.html', error="Error with playlist id")

        if not curr_user_id:
            return render_template('playlist_list.html', error="Error with session user id")

        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                    DELETE FROM playlist_followers 
                    WHERE pf_playlistid = %s
                """
            cur.execute(query, (playlist_id,))

            query = """
                    DELETE FROM playlist 
                    WHERE p_playlistid = %s AND p_author_userid = %s
                """
            cur.execute(query, (playlist_id, curr_user_id))
            conn.commit()

        return redirect(url_for('playlist_list_page.user_playlists'))
    
    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist_list.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)
