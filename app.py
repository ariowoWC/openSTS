from flask import Flask, render_template, request, redirect, session, make_response
import os
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/22240/PycharmProjects/openSTS/openSTS_data"
app.secret_key = '284193f6c8b91412f1aca22df5bab32f21fe895e9a26006b0ac679da12fad160'


def connect_database(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        print("error has occurred while connecting to the database")
    return


@app.route('/', methods=['POST', 'GET'])
def render_homepage():
    if request.method == 'POST':
        user_email = request.form.get('user_email').lower().strip()
        user_password = request.form.get('user_password')

        query = "SELECT user_id, user_email, user_password FROM user WHERE user_email = ?"

        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (user_email,))
        user_info = cur.fetchall()
        con.close()
        print(user_info[0][2])


        try:
            user_email = user_info[0][1]
            db_password = user_info[0][2]

        except IndexError:
            print("invalid email")
            return redirect('/login?error=invalid+email+or+password')

        if db_password != user_password:
            print("invalid password")
            return redirect('/login?error=invalid+email+or+password')

        session['user_email'] = user_email

        return redirect('/')
    return render_template('landing.html')


@app.route('/signup', methods=['POST', 'GET'])
def render_tutor_signup_page():
    if request.method == 'POST':
        tutor_fname = request.form.get('user_fname').title().strip()
        tutor_lname = request.form.get('user_lname').title().strip()
        tutor_email = request.form.get('user_email').lower().strip()
        tutor_password = request.form.get('user_password')

        con = connect_database(DATABASE)
        query_insert = "INSERT INTO user (user_fname, user_lname, user_email, user_password) VALUES (?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query_insert, (tutor_fname, tutor_lname, tutor_email, tutor_password))
        con.commit()
        con.close()

    return render_template('signup.html')


if __name__ == '__main__':
    app.run()
