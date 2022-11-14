#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
"Data Jobs" - Website for staffing and 'upskilling'
br2598
wdw2117

--------------
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
---------------
"""

import os
import uuid
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, flash, session
from werkzeug.security import generate_password_hash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "br2598"
DB_PASSWORD = "miata"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS pika_table;""")
engine.execute("""CREATE TABLE IF NOT EXISTS pika_table (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO pika_table(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    #
    # example of a database query
    #

    cursor = g.conn.execute("SELECT name FROM pika_table")
    names = []
    for result in cursor:
        names.append(result['name'])  # can also be accessed using result[0]
    cursor.close()

    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)


#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
    return render_template("anotherfile.html")


@app.before_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    uid = session.get("uid")

    if uid is None:
        g.user = None
    else:
        g.user = (
            g.conn().execute("SELECT * FROM user WHERE uid = %s", (uid,)).fetchone()
        )


# Example of adding new data to the database


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print(name)
    cmd = 'INSERT INTO pika_table(name) VALUES (:name1)';
    g.conn.execute(text(cmd), name1=name);
    return redirect('/')


#
# CODE DERIVED FROM https://flask.palletsprojects.com/en/2.2.x/tutorial

# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS pika_table;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS pika_table (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO pika_table(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

# def add():
#     name = request.form['name']
#     print(name)
#     cmd = 'INSERT INTO pika_table(name) VALUES (:name1)';
#     g.conn.execute(text(cmd), name1=name);
#     return redirect('/')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == "POST":
#         users_login = request.form['users_login']
#         print(users_login)
#         users_password = request.form['users_password']
#         print(users_password)
#         cmd1 = 'INSERT INTO users(users_login) VALUES (:users_login1)';
#         g.conn.execute(text(cmd1), users_login1=users_login);
#         cmd2 = 'INSERT INTO users(users_password) VALUES (:users_password1)';
#         g.conn.execute(text(cmd2), users_password1=users_password);
#         return redirect('register.html')
# #

@app.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.
    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        users_login = request.form['users_login']
        print(users_login)
        users_password = request.form['users_password']
        print(users_password)
        error = None

        if not users_login:
            error = "Username is required."
        elif not users_password:
            error = "Password is required."
        # Must execute all commands in one line.
        if error is None:
            try:
                # insert_login = 'INSERT INTO users(users_login) VALUES (:users_login1)';
                # g.conn.execute(text(insert_login), users_login1=users_login);
                #
                # insert_password = 'INSERT INTO users(users_password) VALUES (:users_password1)';
                # g.conn.execute(text(insert_password), users_password1=users_password);
                #
                # insert_uid = 'INSERT INTO users(uid) SELECT MAX(uid) +1 FROM Users';
                # g.conn.execute(insert_uid);
                g.conn.execute(
                    "INSERT INTO users (users_login, users_password, uid) VALUES (%s, %s, %s)",
                    (users_login, users_password, uuid.uuid4()),
                )
                # g.conn.commit()
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {login} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("login"))

        flash(error)

    return render_template("register.html")


##


# CODE DERIVED FROM https://flask.palletsprojects.com/en/2.2.x/tutorial
# difference between session.execute and engine.execute
# https://stackoverflow.com/questions/47190680/sqlalchemy-exc-programmingerror-psycopg2-programmingerror-syntax-error-at-or
# solves error sqlalchemy.exc.ProgrammingError: (psycopg2.errors.SyntaxError) syntax error at or near ":"
# LINE 1: SELECT * FROM users WHERE users_login = :users_login
@app.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    if request.method == "POST":
        users_login = request.form["users_login"]
        users_password = request.form["users_password"]
        error = None
        users = g.conn.execute(
            "SELECT * FROM users WHERE users_login = %s", (users_login,)
        ).fetchone()

        # users = g.conn.execute(text(
        #     'SELECT * FROM users WHERE users_login = :users_login', {users_login})
        # ).fetchone()
        #
        # users = 'INSERT INTO users(users_login) VALUES (:users_login1)';
        # g.conn.execute(text(insert_login), users_login1=users_login).fetchone();

        if users is None:
            error = "Incorrect username."
        elif not (users["users_password"], users_password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = users["uid"]
            return redirect(url_for("/"))

        flash(error)

    return render_template("login.html")


@app.route("/upload_job", methods=("GET", "POST"))
def upload_job():
    """Register a new job.
    Validates that the username is not already taken. Hashes the
    password for security.
    """
    #jobtypes_server = g.conn.execute("SELECT DISTINCT job_type FROM DataJobs_Belong ORDER BY job_type ASC")
    jobtypes_server = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer']
    if request.method == "POST":
        company = request.form['company']
        print(company)

        location = request.form['location']
        print(location)

        position_name = request.form['position_name']
        print(position_name)

        salary = request.form['salary']
        print(salary)

        job_type = request.form['job_type']  # dropdown 4 choices
        print(job_type)

        error = None

        if not company:
            error = "Company is required."
        elif not location:
            error = "Location is required."
        elif not position_name:
            error = "Position name is required."
        elif not salary:
            error = "Salary is required"
        elif not job_type:
            error = "Job type is required."

        # Must execute all commands in one line.
        if error is None:
            try:
                g.conn.execute(
                    "INSERT INTO DataJobs_Belong (company, location, position_name, salary, job_type, job_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (company, location, position_name, salary, job_type, uuid.uuid4()),
                    # job_id is primary key, but incrementing +1 is not secure.
                    # uuid generates random non-conflicting id.
                )
                # g.conn.commit()
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {login} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("index"))

        flash(error)

    return render_template("upload_job.html", jobtypes_server=jobtypes_server)


@app.route("/upload_ads", methods=("GET", "POST"))
def upload_ads():
    """Register a new ad.

    """
    if request.method == "POST":
        target_audience = request.form['target_audience']
        print(target_audience)

        ad_cost = request.form['ad_cost']
        print(ad_cost)

        ad_position = request.form['ad_position']
        print(ad_position)

        error = None

        if not target_audience:
            error = "Target audience is required."
        elif not ad_cost:
            error = "Ad cost is required."
        elif not ad_position:
            error = "Ad position is required."

        # Must execute all commands in one line.
        if error is None:
            try:
                g.conn.execute(
                    "INSERT INTO Ads (target_audience, ad_cost, ad_position, ad_id)"
                    "VALUES (%s, %s, %s, %s)",
                    (target_audience, ad_cost, ad_position, uuid.uuid4()),
                )
                # g.conn.commit()
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {login} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("login"))

        flash(error)

    return render_template("upload_ads.html")


#
# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


@app.route("/update", methods=("GET", "POST"))
def update_users():
    if request.method == 'POST':
        print(request.form.getlist('mycheckbox'))
        return 'Done'
    return render_template("update.html")


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """
        app.secret_key = 'super secret key'
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
