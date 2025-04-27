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
                        return render_template('login.html', error="Incorrect username or password.")
                    else:
                        return redirect(url_for('home'))
        except Exception as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return render_template('home.html')
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
