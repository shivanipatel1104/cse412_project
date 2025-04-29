from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

profile_page = Blueprint('profile_page', __name__)

@profile_page.route('/', methods=['GET'])
def profile():
	return render_template('profile.html')	
