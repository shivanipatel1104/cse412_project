from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2
from enum import Enum
from datetime import datetime

# defining enum type for clearer handling of button logic
class PlaylistType(Enum):
    TOP10_LIST = 'top10_list' # to show top 10 most followed playlists
    USER_LIST = 'user_list' # to show playlists current user follows
    CREATE_PLAYLIST = 'create_playlist' # to show pop up to create playlist

playlist_list_page = Blueprint('playlist_list_page', __name__)

# Function shows a list of playlists to the user. There are two types of lists:
#       --> Playlist user follows (default if no button is pressed)
#       --> Top 10 most followed playlists
# Which list is shown is decided by which button is pressed (request named 'button_click')
@playlist_list_page.route('/', methods=['GET', 'POST'])
def user_playlists():
    # Intitializing values
    playlists = []
    button_type = PlaylistType.USER_LIST # user list is default

    # fetch user id for current user from session
    curr_user_id = session.get('user_id')
    if not curr_user_id:
        return redirect(url_for('login_page.login'))
    try:
        conn = get_db_connection()

        with conn.cursor() as cur:
            button_string = request.form.get("button_click") # ***fetch which button was clicked ("button_click" is input name)***

            if button_string:
                try:
                    button_type = PlaylistType(button_string)
                except ValueError:
                    button_type = PlaylistType.USER_LIST # use default case in case of unknown behavior

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

            # button for creating a playlist
            elif button_type == PlaylistType.CREATE_PLAYLIST:
                playlist_name = request.form.get("playlist_name")
                author_id = session.get('user_id') # author of playlist is current user
                time_created = datetime.now()

                if not playlist_name:
                    raise Exception("Playlist name required")

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

                # I needed to make sure that when a playlist was created, it was
                # also added to the creator's followed playlist table in the db

                cur.execute(playlist_query, (playlist_name, author_id, time_created))
                conn.commit()

                cur.execute(get_playlist_id_query, (playlist_name, author_id))
                playlist_id_data = cur.fetchone()

                cur.execute(playlist_follower_query, (playlist_id_data, author_id))
                conn.commit()

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

    #Using button_type parameter for easier rendering of correct list
    return render_template('playlist_list.html', playlists=playlists, button_type=button_type)

@playlist_list_page.route('/select_playlist', methods=['POST'])
def playlist_select_handler():
    try:
        playlist_id = request.form.get("playlist_select")

        if not playlist_id:
            raise Exception("Invalid playlist selected")

        session['playlist_id'] = playlist_id
        return redirect(url_for('playlist_page.playlist_info'))

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('playlist_list.html', error=message)         

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('playlist_list.html', error=message)

