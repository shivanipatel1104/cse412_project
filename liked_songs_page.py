from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

liked_songs_page = Blueprint('liked_songs_page', __name__)

# Selecting liked songs
@liked_songs_page.route('/', methods=['GET'])
def liked_songs():
	try:
		user_id = session.get('user_id')
		if not user_id:
			return render_template('login.html')

		conn = get_db_connection()
		with conn.cursor() as cur:
			query = """
				SELECT s_songID, s_songname, al_albumName, a_artistName
				FROM song
				JOIN album ON s_albumID = al_albumID
				JOIN artist ON al_artistID = a_artistID
				JOIN likedsongs ON l_songID = s_songID
				WHERE l_userID = %s;
			"""
			cur.execute(query, (user_id,))
			songs = cur.fetchall()

			if not songs:
				message = "No liked songs for your account."
				return render_template('liked_songs.html', error=message)
			

	except psycopg2.DatabaseError as e:
		message = f"Database error: {str(e)}"
		return render_template('liked_songs.html', error=message)

	except Exception as e:
		message = f'Error when handling request: {str(e)}'
		return render_template('liked_songs.html', error=message)

	finally:
		if conn:
			conn.close()

	return render_template('liked_songs.html', songs=songs)

@liked_songs_page.route('/delete_like', methods = ['POST'])
def delete_liked_song():
    try:
        song_id = request.form.get('liked_song')
        user_id = session.get('user_id')

        if not song_id:
            return render_template('liked_songs.html', error="Error: No song session id")

        if not user_id:
            return render_template('liked_songs.html', error="Error: No user session id")

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Get song name
                song_name_query = 'SELECT s_songname FROM song WHERE s_songID = %s'
                cur.execute(song_name_query, (song_id,))
                result = cur.fetchone()

                if result:
                    song_name = result[0]

                else:
                    mess = 'Error: song id does not exist'
                    return render_template('liked_songs.html', error=mess)

                # Checking if song is in user's liked songs
                query = """
                    SELECT *
                    FROM likedsongs
                    WHERE l_userID = %s AND l_songID = %s
                """
                cur.execute(query, (user_id, song_id))
                is_liked = cur.fetchone()

                # If is in user's liked songs, then remove it
                if is_liked:
                    message = f"{song_name} removed from liked songs!"
                    query = """
                        DELETE FROM likedsongs
                        WHERE l_userID = %s AND l_songID = %s 
                    """
                    cur.execute(query, (user_id, song_id))

                # Fetch song data for message
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
                    return render_template('liked_songs.html', error='Unknown song name')
                
                session['song_liked_message'] = message

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('liked_songs.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('liked_songs.html', error=message)

    return redirect(url_for('liked_songs_page.liked_songs'))
