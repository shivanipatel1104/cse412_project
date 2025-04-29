from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

liked_songs_page = Blueprint('liked_songs_page', __name__)

@liked_songs_page.route('/', methods=['GET'])
def liked_songs():
	return render_template('liked_songs.html')