from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

playlist_page = Blueprint('playlist_page', __name__)

@playlist_page.route('/', methods=['GET', 'POST'])
def playlist_info():
	playlist_id = session.get('playlist_id')

	if not playlist_id:
		return redirect(url_for('playlist_list_page.user_playlists'))

	return render_template('playlist.html', playlist_id=playlist_id)