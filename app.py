from flask import Flask, render_template, request, redirect, session, make_response
from datetime import datetime
import os
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

DATABASE = "C:/Users/22240/PycharmProjects/openSTS/openSTS_data"
app.secret_key = '284193f6c8b91412f1aca22df5bab32f21fe895e9a26006b0ac679da12fad160'
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"


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
    return redirect("/home")
    print(session.get("user_type"))


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    if request.method == 'POST':
        user_email = request.form.get('user_email').lower().strip()
        user_password = request.form.get('user_password')

        query = "SELECT user_id, user_email, user_password, user_type FROM user WHERE user_email = ?"

        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (user_email,))
        user_info = cur.fetchall()
        con.close()
        user_type = user_info[0][3]
        print(user_type)
        print

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
        session['user_type'] = user_type

        print(session.get("user_type"))

        return redirect('/home')
    return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def render_tutor_signup_page():
    if request.method == 'POST':
        tutor_fname = request.form.get('user_fname').title().strip()
        tutor_lname = request.form.get('user_lname').title().strip()
        tutor_email = request.form.get('user_email').lower().strip()
        tutor_password = request.form.get('user_password')

        con = connect_database(DATABASE)
        query_insert = "INSERT INTO user (user_fname, user_lname, user_email, user_password, user_type) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query_insert, (tutor_fname, tutor_lname, tutor_email, tutor_password, "user"))
        con.commit()
        con.close()
        return redirect('/')
    return render_template('signup.html')


@app.route('/home')
def render_authed_base():
    session.get("user_email")
    return render_template('home.html')


@app.route('/dashboard')
def render_dashboard():
    user_email = session.get("user_email")
    user_type = session.get("user_type")
    print(user_type)

    if not user_email:
        return redirect("/login")

    if user_type == "user":
        con = connect_database(DATABASE)
        query = "SELECT ticket_id, ticket_user, ticket_type, ticket_desc FROM tickets WHERE ticket_user = ?"
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (user_email,))
        tickets_data = cur.fetchall()
        print(tickets_data)
        con.close()

    if user_type == "admin":
        con = connect_database(DATABASE)
        query = "SELECT ticket_id, ticket_user, ticket_type, ticket_desc FROM tickets"
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query)
        tickets_data = cur.fetchall()
        print(tickets_data)
        con.close()

    return render_template("dashboard.html", tickets=tickets_data)

@app.route('/addticket', methods=['POST', 'GET'])
def render_add_ticket():
    if request.method == 'POST':
        ticket_type = request.form.get('ticket_type')
        ticket_desc = request.form.get('ticket_desc')
        ticket_user = session.get("user_email")
        ticket_time = datetime.utcnow().timestamp()

        con = connect_database(DATABASE)
        query_insert = "INSERT INTO tickets (ticket_user, ticket_time, ticket_type, ticket_desc) VALUES (?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query_insert, (ticket_user, ticket_time, ticket_type, ticket_desc))
        con.commit()
        con.close()

    return render_template('addticket.html')


@app.route("/signout")
def logout():
    session["user_email"] = None
    return redirect("/")


if __name__ == '__main__':
    app.run()
