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
				SELECT s_songname, al_albumName, a_artistName
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

