from flask import Flask, render_template, Blueprint

views = Blueprint(__name__, 'views')


@views.route('/')
def home():
    return render_template('index.html', author='Christian')