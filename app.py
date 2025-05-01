from flask import Flask
from login_page import login_page
from sign_up_page import sign_up_page
from home_page import home_page
from playlist_list_page import playlist_list_page
from playlist_page import playlist_page
from search_page import search_page
from liked_songs_page import liked_songs_page
from profile_page import profile_page
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# Register blueprints
app.register_blueprint(login_page, url_prefix='/')
app.register_blueprint(sign_up_page, url_prefix='/signup')
app.register_blueprint(home_page, url_prefix='/home')
app.register_blueprint(playlist_list_page, url_prefix='/playlist_list')
app.register_blueprint(playlist_page, url_prefix='/playlist')
app.register_blueprint(search_page, url_prefix='/search')
app.register_blueprint(liked_songs_page, url_prefix='/liked_songs')
app.register_blueprint(profile_page, url_prefix='/profile')

if __name__ == '__main__':
    app.run(debug=True)