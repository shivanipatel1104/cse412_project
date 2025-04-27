
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return render_template('home.html')
    return render_template('login.html')  # or whatever your one page is called

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
