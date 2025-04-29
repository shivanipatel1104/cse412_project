from flask import Flask, render_template
from login_page import login_page
from sign_up_page import sign_up_page
from home_page import home_page
from playlist_list_page import playlist_list_page
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# Register blueprints
app.register_blueprint(login_page, url_prefix='/')
app.register_blueprint(sign_up_page, url_prefix='/signup')
app.register_blueprint(home_page, url_prefix='/home')
app.register_blueprint(playlist_list_page, url_prefix='/playlist_list')


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/likedsongs', endpoint='likedsongs')
def likedsongs():
    return render_template('likedsongs.html')

if __name__ == '__main__':
    app.run(debug=True)
