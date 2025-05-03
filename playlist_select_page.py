from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

playlist_select_page = Blueprint('playlist_select_page', __name__)


@playlist_select_page.route('/', methods=['GET'])
def show_playlists():
	try:
		user_id = session.get('user_id')

		conn = get_db_connection()
		with conn.cursor() as cur:
			query = """
				SELECT p_playlistID, p_playlistname
				FROM playlist
				WHERE p_author_userid = %s
			"""
			cur.execute(query, (user_id,))
			playlists = cur.fetchall()

	except Exception as e:
		mess = f'Error when handling request: {str(e)}'
		return render_template('playlist_select.html', error=mess)

	return render_template('playlist_select.html', playlists=playlists)

@playlist_select_page.route('/playlist_selected', methods=['POST'])
def playlist_selected():
	try:
		playlist_id = request.form.get('playlist_id')
		song_id = session.get('song_id')

		if not song_id:
			return render_template('playlist_select.html', error='Error with song id session')

		conn = get_db_connection()
		with conn.cursor() as cur:
			query = """
				INSERT INTO playlistsongs (ps_playlistID, ps_songID)
				VALUES (%s, %s)
			"""
			cur.execute(query, (playlist_id, song_id))
			conn.commit()

	except Exception as e:
		mess = f'Error when handling request: {str(e)}'
		return render_template('playlist_select.html', error=mess)

	return redirect(url_for('playlist_list_page.user_playlists'))