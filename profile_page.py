from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

profile_page = Blueprint('profile_page', __name__)

@profile_page.route('/', methods=['GET'])
def profile():
	try:
		conn = get_db_connection()
		with conn.cursor() as cur:
			user_id = session.get('user_id')
			if not user_id:
				mess = 'User login credentials not found'
				return render_template('profile.html', message=mess)

			query = """
				SELECT u_username, u_name, u_email
				FROM user
				WHERE u_userID = %s
			"""
			cur.execute(query, (user_id,))
			user_info = cur.fetchone()

			if not user_info:
				message = 'User info not found'
				render_template('profile.html', error=message)
    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('search.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('search.html', error=message)

    finally:
    	if conn:
    		conn.close()

	return render_template('profile.html', user_info=user_info)
