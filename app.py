from flask import Flask
from login_page import login_page
from sign_up_page import sign_up_page
from home_page import home_page
import secrets


app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

# Register blueprints
app.register_blueprint(login_page, url_prefix='/')
app.register_blueprint(sign_up_page, url_prefix='/signup')
app.register_blueprint(home_page, url_prefix='/home')

if __name__ == '__main__':
    app.run(debug=True)
