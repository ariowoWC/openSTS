from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error

app = Flask(__name__)


@app.route('/')
def render_homepage():
    return render_template('landing.html')


if __name__ == '__main__':
    app.run()
