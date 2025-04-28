from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        dbname='music_app',
        user='postgres',
        password='0411BPTp',
        port='5432'
    )
# TODO: Right now, if the user entered a previously used email or username, then they
# have to re-enter all the fields again. If time, try to find way so that fields are not
# all reset.
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection()
            with conn:
                with conn.cursor() as cur:
                    query = "SELECT u_userID FROM users WHERE u_username = %s AND u_password = %s"
                    cur.execute(query, (username, password))
                    login_status = cur.fetchone()
                    if not login_status:
                        return render_template('login.html', error="Incorrect login credentials.")
                    else:
                        return redirect(url_for('home'))
        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
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
                    return redirect(url_for('home'))

        except Exception as e:
            message = f"Account creation failed: {str(e)}"
            return render_template('signup.html', error=message)

    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
