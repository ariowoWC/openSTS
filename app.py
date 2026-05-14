from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
import bleach

app = Flask(__name__)
bcrypt = Bcrypt(app)

DATABASE = "C:/Users/Bach/Documents/openSTS/openSTS_data.db3"  # set database path here
app.secret_key = '284193f6c8b91412f1aca22df5bab32f21fe895e9a26006b0ac679da12fad160'
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"


@app.template_filter()
def format_datetime(timestamp):
    """
    converts unix timestamp to readable datetime
    :param timestamp:
    :return: formatted_datetime
    """
    formatted_datetime = datetime.fromtimestamp(int(timestamp))  # converts unix timestamp to standard datetime
    return formatted_datetime


def connect_database(db_file):
    """
    establishes a connection to the database
    :param db_file:
    :return:
    """
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
        print("error has occurred while connecting to the database")
    return


@app.route('/', methods=['POST', 'GET'])
def render_homepage():
    """
    redirects the user to the homepage
    :return:
    """
    return redirect("/home")


@app.route('/login', methods=['POST', 'GET'])
def render_login():
    """
    renders the login page and validates login data
    :return: user id, email, password and type
    """
    if request.method == 'POST':
        user_email = bleach.clean(request.form.get('user_email').lower().strip())
        user_password = bleach.clean(request.form.get('user_password'))
        # takes the email and password from the input form, sanitizes it with Bleach and assigns it to a variable

        query = "SELECT user_id, user_email, user_password, user_type FROM user WHERE user_email = ?"

        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (user_email,))
        user_info = cur.fetchall()
        con.close()

        try:
            user_email = user_info[0][1]
            user_type = user_info[0][3]
            # checks if the provided email exists

        except IndexError:
            print("invalid email")
            return redirect('/login?error=invalid+email')

        if not bcrypt.check_password_hash(user_info[0][2], user_password):
            print("invalid password")
            return redirect('/login?error=invalid+password')
            # compares the provided password's hash to one pulled from the database

        session['user_email'] = user_email
        session['user_type'] = user_type
        # turns user info into a cookie if authentication successful

        print(session.get("user_type"))

        return redirect('/home')
    return render_template("login.html")


@app.route('/signup', methods=['POST', 'GET'])
def render_tutor_signup_page():
    """
    renders the signup page for users
    :return: user id, name, email and password hash
    """
    if request.method == 'POST':
        user_fname = bleach.clean(request.form.get('user_fname').title().strip())
        user_lname = bleach.clean(request.form.get('user_lname').title().strip())
        user_email = bleach.clean(request.form.get('user_email').lower().strip())
        user_password = bcrypt.generate_password_hash(request.form.get('user_password'))
        # takes the email and password from the input form, sanitizes it with Bleach and assigns it to a variable

        query_insert = "INSERT INTO user (user_fname, user_lname, user_email, user_password, user_type) "\
                       "VALUES (?, ?, ?, ?, ?)"

        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query_insert, (user_fname, user_lname, user_email, user_password, "user"))
        con.commit()
        con.close()
        return redirect('/')
    return render_template('signup.html')


@app.route('/adduser', methods=['POST', 'GET'])
def add_user():
    """
    renders a page to add users. only accessible by administrators
    :return: user id, email, password, privilege, name
    """
    user_type = session.get("user_type")
    if user_type != "admin":
        return redirect("/home")
    
    if request.method == 'POST':
        fname = bleach.clean(request.form.get('fname').title().strip())
        lname = bleach.clean(request.form.get('lname').title().strip())
        email = bleach.clean(request.form.get('email').lower().strip())
        password = bcrypt.generate_password_hash(request.form.get('password'))
        user_role = bleach.clean(request.form.get('user_type'))
        # takes the email and password from the input form, sanitizes it with Bleach and assigns it to a variable

        query = "INSERT INTO user (user_fname, user_lname, user_email, user_password, user_type) VALUES (?, ?, ?, ?, ?)"
        
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (fname, lname, email, password, user_role))
        con.commit()
        con.close()
        
        return redirect('/adduser?success=User+added')
    
    return render_template('adduser.html')


@app.route('/home')
def render_authed_base():
    """
    renders the home page and displays the logged in user's email and privilege level
    :return: user email, user type
    """
    session.get("user_email")
    session.get("user_type")
    return render_template('home.html')


@app.route('/dashboard')
def render_dashboard():
    """
    renders dashboard and displays relevant tickets
    :return: ticket_id, ticket_user, ticket_type, ticket_desc, ticket_time
    """
    user_email = session.get("user_email")
    user_type = session.get("user_type")
    print(user_type)

    if not user_email:
        return redirect("/login")
        # checks for login cookie and redirects user to the login page if not present

    if user_type == "user":  # grabs relevant tickets if current user is a standard user
        query = "SELECT ticket_id, ticket_user, ticket_type, ticket_desc, ticket_time " \
                "FROM tickets WHERE ticket_user = ?"
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query, (user_email,))
        tickets_data = cur.fetchall()
        print(tickets_data)
        con.close()

    if user_type == "admin":  # grabs all tickets if current user is admin
        query = "SELECT ticket_id, ticket_user, ticket_type, ticket_desc, ticket_time FROM tickets"
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query)
        tickets_data = cur.fetchall()
        print(tickets_data)
        con.close()

    return render_template("dashboard.html", tickets=tickets_data)


@app.route('/addticket', methods=['POST', 'GET'])
def render_add_ticket():
    """
    renders a ticket creation page
    :return: ticket_user, ticket_time, ticket_type, ticket_desc
    """
    if not session.get("user_email"):
        return redirect("/login")
    if request.method == 'POST':
        ticket_type = request.form.get('ticket_type')
        ticket_desc = request.form.get('ticket_desc')
        ticket_user = session.get("user_email")
        ticket_time = datetime.utcnow().timestamp()
        # pulls info from the form and assigns them to a variable

        con = connect_database(DATABASE)
        query_insert = "INSERT INTO tickets (ticket_user, ticket_time, ticket_type, ticket_desc) VALUES (?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query_insert, (ticket_user, ticket_time, ticket_type, ticket_desc))
        con.commit()
        con.close()
        return redirect("/dashboard")

    return render_template('addticket.html')


@app.route("/signout")
def render_logout():
    """
    logs user out
    :return:
    """
    session["user_email"] = None
    # sets the user cookie to null, effectively logging them out
    return redirect("/")


@app.route("/ticket/<int:ticket_id>", methods=['GET', 'POST'])
def render_ticket_detail(ticket_id):
    """
    renders a detailed view of a selected ticket
    :param ticket_id:
    :return: reply_id, reply_user, reply_text, reply_time, ticket_desc
    """
    user_email = session.get("user_email")
    if not user_email:
        return redirect("/login")
    
    con = connect_database(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT ticket_id, ticket_user, ticket_type, ticket_desc, ticket_time FROM tickets "
                "WHERE ticket_id = ?", (ticket_id,))
    ticket = cur.fetchone()
    
    cur.execute("SELECT reply_id, reply_user, reply_text, reply_time FROM replies "
                "WHERE ticket_id = ? ORDER BY reply_time DESC", (ticket_id,))
    replies = cur.fetchall()
    con.close()
    
    if not ticket:  # redirects user if ticket doesn't exist
        return redirect("/dashboard?error=ticket+not+found")
    
    user_type = session.get("user_type")
    if user_type != "admin" and ticket[1] != user_email:  # if isn't ticket creator or isn't admin, access is denied
        return redirect("/dashboard?error=unauthorized")
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'edit':
            new_desc = bleach.clean(request.form.get('ticket_desc'))  # sanitizes edit contents
            con = connect_database(DATABASE)
            cur = con.cursor()

            cur.execute("UPDATE tickets SET ticket_desc = ? WHERE ticket_id = ?", (new_desc, ticket_id))

            con.commit()
            con.close()
            return redirect(f"/ticket/{ticket_id}?success=ticket+updated")
        
        elif action == 'delete':
            con = connect_database(DATABASE)
            cur = con.cursor()

            cur.execute("DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,))

            con.commit()
            con.close()
            return redirect("/dashboard?success=ticket+deleted")
    
    return render_template('ticket_detail.html', ticket=ticket, replies=replies)


@app.route("/addreply/<int:ticket_id>", methods=['POST'])
def add_reply(ticket_id):
    """
    renders the page to add replies
    :param ticket_id:
    :return: ticket_id, reply_user, reply_text, reply_time
    """
    user_email = session.get("user_email")
    if not user_email:  # if user is not logged in, they are redirected to the login page
        return redirect("/login")
    
    reply_text = bleach.clean(request.form.get('reply_text'))  # sanitizes reply text
    reply_time = datetime.utcnow().timestamp()
    
    con = connect_database(DATABASE)
    cur = con.cursor()

    cur.execute("INSERT INTO replies (ticket_id, reply_user, reply_text, reply_time) "
                "VALUES (?, ?, ?, ?)", (ticket_id, user_email, reply_text, reply_time))

    con.commit()
    con.close()
    
    return redirect(f"/ticket/{ticket_id}?success=reply+added")


if __name__ == '__main__':
    app.run()
