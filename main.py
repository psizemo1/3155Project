from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/about')
def about():
    return render_template('about.html')
