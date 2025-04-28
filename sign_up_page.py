from flask import Blueprint, render_template, request, redirect, url_for
from database import get_db_connection
import psycopg2

sign_up_page = Blueprint('sign_up_page', __name__)

@sign_up_page.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            with conn:
                with conn.cursor() as cur:
                    email_check = """
                        SELECT u_email
                        FROM users
                        WHERE u_email = %s
                    """
                    cur.execute(email_check, (email,))
                    email_exists = cur.fetchone()

                    if email_exists:
                        message = f"{email} is already used, please pick another email."
                        return render_template('signup.html', error = message)

                    username_check = """
                        SELECT u_username
                        FROM users
                        WHERE u_username = %s
                    """
                    cur.execute(username_check, (username,))
                    username_exists = cur.fetchone()

                    if username_exists:
                        message = f"{username} is already used, please pick another username"
                        return render_template('signup.html', error = message)

                    query = """
                        INSERT INTO users (u_username, u_name, u_email, u_password, u_usertype) 
                        VALUES (%s, %s, %s, %s, 'user')
                    """
                    cur.execute(query, (username, name, email, password))
                    conn.commit()
                    return redirect(url_for('login_page.login'))

        except Exception as e:
            message = f"Account creation failed: {str(e)}"
            return render_template('signup.html', error=message)

    return render_template('signup.html')
