from flask import Blueprint, render_template, request, redirect, url_for, session
from database import get_db_connection
import psycopg2

login_page = Blueprint('login_page', __name__)

@login_page.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                query = "SELECT u_userID FROM users WHERE u_username = %s AND u_password = %s"
                cur.execute(query, (username, password))
                login_data = cur.fetchone()
                if not login_data:
                    return render_template('login.html', error="Incorrect username or password.")
                else:
                    session['user_id'] = login_data[0]
                    return redirect(url_for('home_page.home'))  

        except psycopg2.DatabaseError as e:
            message = f"Database error: {str(e)}"
            return render_template('login.html', error=message)

        except Exception as e:
            message = f'Error when handling request: {str(e)}'
            return render_template('login.html', error=message)

    return render_template('login.html')
