from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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
                FROM users
                WHERE u_userID = %s
            """
            cur.execute(query, (user_id,))
            user_info = cur.fetchone()

            if not user_info:
                message = 'User info not found'
                return render_template('profile.html', error=message)

    except psycopg2.DatabaseError as e:
        message = f"Database error: {str(e)}"
        return render_template('profile.html', error=message)

    except Exception as e:
        message = f'Error when handling request: {str(e)}'
        return render_template('profile.html', error=message)

    finally:
        if conn:
            conn.close()

    return render_template('profile.html', user_info=user_info)

@profile_page.route('/change_password', methods=['POST'])
def change_password():
    try:
        user_id = session.get('user_id')
        new_password = request.form.get("new_password")
        if not new_password:
            return render_template('profile.html', error='Password field required')

        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                UPDATE users 
                SET u_password = %s 
                WHERE u_userID = %s
            """
            cur.execute(query, (new_password, user_id))
            conn.commit()

    except Exception as e:
        return render_template('profile.html', error = f'Error: {str(e)}')

    finally:
        conn.close()

    flash('Password was successfully changed!')
    return redirect(url_for('profile_page.profile'))

@profile_page.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login_page.login'))
