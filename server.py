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


#
# class UsersClass(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#
#     def __repr__(self):
#         return '<User %r>' % self.username


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


@app.route("/search", methods=("GET", "POST"))
# For william
def search():
    """
    Query for all jobs of a given type.
    Works but is messy
    ('8', 'WorkFusion', '3dc2f5949913c1b7', 'New York, NY 10005', 'Machine Learning Engineer', None, 'ML Engineer', True, False, False, True, False, False, False, False, False, True, False, False, False, True, False)

    Ideally would just output
    -
    Company: Workfusion
    Location: New York
    Title: Machine Learning Engineer
    Salary: None
    Job Type: ML Engineer
    -

    """
    jobtypes_server = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer']

    if request.method == "POST":
        job_type = request.form["job_type"]
        print(job_type)
        error = None

        if not job_type:
            error = "Job search is required."

        if error is None:
            try:
                cursor = g.conn.execute("SELECT * FROM datajobs_belong "
                                        "WHERE job_type =  %s", job_type)
                names = []
                for result in cursor:
                    names.append(result)  # result[0] = uid, result [1] = company, and so on...
                cursor.close()
                context = dict(data=names)
                return render_template("search.html", jobtypes_server=jobtypes_server, **context)
            finally:
                print("The try...except block is finished")

    else:
        return render_template("search.html", jobtypes_server=jobtypes_server)


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
    #desired_role = session["desired_role"]

    if uid is None:
        g.user = None
    else:
        # g.user = (
        #     g.conn().execute("SELECT * FROM users WHERE uid = %s"), user_id
        # )
        g.user = g.conn.execute(
            "SELECT * FROM users WHERE uid = %s", (uid,)
        ).fetchone()


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    print(name)
    cmd = 'INSERT INTO pika_table(name) VALUES (:name1)';
    g.conn.execute(text(cmd), name1=name);
    return redirect('/')


#
# CODE DERIVED FROM https://flask.palletsprojects.com/en/2.2.x/tutorial


@app.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.
    Validates that the username is not already taken. - DOES NOT WORK
    """
    user_desired_roles = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer']
    bool_list = ['TRUE', 'FALSE']
    deg_list = ['None', 'High School/GED', 'Associate', 'Bachelors', 'Masters', 'PHD', 'Secret Clown College']

    user_roles = ['I am seeking employment!', 'I am a company uploading jobs!', 'I am an advertiser!', 'I am an admin!']
    user_dict = {
        'I am seeking employment!': '1',
        'I am a company uploading jobs!': '2',
        'I am an advertiser!': '3',
        'I am an admin!': '4'
    }

    if request.method == "POST":
        users_login = request.form['users_login']
        print(users_login)

        users_password = request.form['users_password']
        print(users_password)

        users_role = request.form['account_type']

        #
        desired_role = request.form['desired_role']
        print(desired_role)

        education_level = request.form['education_level']
        print(education_level)

        email = request.form['email']
        print(email)

        full_name = request.form['full_name']
        print(full_name)

        # SKILLS #
        python = request.form['python']
        print(python)

        scala = request.form['scala']
        print(scala)

        java = request.form['java']
        print(java)

        excel = request.form['excel']
        print(excel)

        powerpoint = request.form['powerpoint']
        print(powerpoint)

        google_analytics = request.form['google_analytics']
        print(google_analytics)

        matlab = request.form['matlab']
        print(matlab)

        power_bi = request.form['power_bi']
        print(power_bi)

        tableau = request.form['tableau']
        print(tableau)

        aws = request.form['aws']
        print(aws)

        hive = request.form['hive']
        print(hive)

        spark = request.form['spark']
        print(spark)

        postgres = request.form['postgres']
        print(postgres)

        azure = request.form['azure']
        print(azure)

        skill_sql = request.form['skill_sql']
        print(skill_sql)

        #
        error = None

        if not users_login:
            error = "Username is required."
        elif not users_password:
            error = "Password is required."
        # Must execute all commands in one line.

        query = g.conn.execute(
            "SELECT * FROM users WHERE users_login = %s", users_login
        )
        rows = query.all()
        count = len(rows)
        if(count > 0):
            return redirect(url_for("register"))

        if error is None:
            try:
                # g.conn.execute(
                #     "INSERT INTO users (users_login, users_password, uid, role_level) "
                #     "VALUES "
                #     "(%s, %s, %s, %s)",
                #     (users_login, users_password, uuid.uuid4(), user_dict[users_role]),
                # )
                #######
                g.conn.execute(
                    "INSERT INTO users "
                    "(users_login, users_password, uid, role_level,"
                    "desired_role, email, full_name, education_level,"
                    "python, scala, java, excel, powerpoint, google_analytics, matlab, power_bi, tableau, aws, hive, "
                    "spark, postgres, azure, skill_sql) "
                    "VALUES "
                    "(%s, %s, %s, %s,"  # 4 login parameters
                    "%s, %s, %s, %s,"  # next 4 user parameters
                    "%s, %s, %s, %s, %s, "  # skills, first 5
                    "%s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s) ",  # skills last 5
                    (users_login, users_password, uuid.uuid4(), user_dict[users_role],  # 4 login parameters
                     desired_role, email, full_name, education_level,  # 4 key parameters
                     python, scala, java, excel, powerpoint,  # first 5
                     google_analytics, matlab, power_bi, tableau, aws,
                     hive, spark, postgres, azure, skill_sql  # last 5
                     )
                )
                #########
                # g.conn.commit()
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {users_login} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("login"))

        flash(error)

    return render_template("register.html", user_roles=user_roles, user_desired_roles=user_desired_roles,
                           bool_list=bool_list, deg_list=deg_list)


##


# CODE DERIVED FROM https://flask.palletsprojects.com/en/2.2.x/tutorial
# difference between session.execute and engine.execute
# https://stackoverflow.com/questions/47190680/sqlalchemy-exc-programmingerror-psycopg2-programmingerror-syntax-error-at-or
# solves error sqlalchemy.exc.ProgrammingError: (psycopg2.errors.SyntaxError) syntax error at or near ":"
# LINE 1: SELECT * FROM users WHERE users_login = :users_login
@app.route("/login", methods=("GET", "POST"))
def login():
    """
    Log in a registered user by adding the user id to the session.
    Test incorrect username/pw
    """
    if request.method == "POST":
        users_login = request.form["users_login"]
        users_password = request.form["users_password"]
        error = None
        users = g.conn.execute(
            "SELECT * FROM users WHERE users_login = %s", (users_login,)
        ).fetchone()

        if users is None:
            error = "Incorrect username."

        elif not (users["users_password"], users_password):
            error = "Incorrect password."

        query = g.conn.execute(
            "SELECT * FROM users WHERE users_password = %s AND users_login = %s", users_password, users_login
        )

        rows = query.all()
        count = len(rows)
        if(count <= 0):
            return redirect(url_for("login"))

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["uid"] = users["uid"]
            session["desired_role"] = users["desired_role"] # match to target audience in training material/ads
            return redirect('/')

        flash(error)

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Clear the current session,
    including the stored user id. - WORKS
    """
    session.clear()
    return redirect(url_for("index"))


@app.route("/upload_job", methods=("GET", "POST"))
def upload_job():
    """
    Register a new job. - WORKS
    Adds the UID of the person uploading the job - WORKS
    """
    # jobtypes_server = g.conn.execute("SELECT DISTINCT job_type FROM DataJobs_Belong ORDER BY job_type ASC")
    jobtypes_server = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer']
    bool_list = ['TRUE', 'FALSE']
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

        # SKILLS #
        python = request.form['python']
        print(python)

        scala = request.form['scala']
        print(scala)

        java = request.form['java']
        print(java)

        excel = request.form['excel']
        print(excel)

        powerpoint = request.form['powerpoint']
        print(powerpoint)

        google_analytics = request.form['google_analytics']
        print(google_analytics)

        matlab = request.form['matlab']
        print(matlab)

        power_bi = request.form['power_bi']
        print(power_bi)

        tableau = request.form['tableau']
        print(tableau)

        aws = request.form['aws']
        print(aws)

        hive = request.form['hive']
        print(hive)

        spark = request.form['spark']
        print(spark)

        postgres = request.form['postgres']
        print(postgres)

        azure = request.form['azure']
        print(azure)

        skill_sql = request.form['skill_sql']
        print(skill_sql)
        # SKILLS #

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
                    "INSERT INTO DataJobs_Belong "
                    "(company, location, position_name, salary, job_type, job_id,"
                    "python, scala, java, excel, powerpoint, google_analytics, matlab, power_bi, tableau, aws, hive, "
                    "spark, postgres, azure, skill_sql, uid) "
                    "VALUES "
                    "(%s, %s, %s, %s, %s, %s,"  # 6 key parameters
                    "%s, %s, %s, %s, %s, "  # skills, first 5
                    "%s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s, "  # skills last 5
                    "%s)",  # uid who uploaded job
                    (company, location, position_name, salary, job_type, uuid.uuid4(),
                     python, scala, java, excel, powerpoint,
                     google_analytics, matlab, power_bi, tableau, aws,
                     hive, spark, postgres, azure, skill_sql, session["uid"]
                     )
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

    return render_template("upload_job.html", jobtypes_server=jobtypes_server, bool_list=bool_list)


@app.route("/upload_ads", methods=("GET", "POST"))
def upload_ads():
    """Register a new ad.

    """

    target_audience_groups = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer', 'Novice']
    ad_cost_dropdown = [100, 200, 300]
    ad_position_options = ['Left', 'Right', 'Footer']

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

    return render_template("upload_ads.html", target_audience_groups=target_audience_groups,
                           ad_cost_dropdown=ad_cost_dropdown, ad_position_options=ad_position_options)


@app.route("/upload_class", methods=("GET", "POST"))
def upload_classes():
    """
    Register a new class.
    """
    if request.method == "POST":
        course_name = request.form['course_name']
        print(course_name)

        error = None

        if not course_name:
            error = "course_name is required."

        # Must execute all commands in one line.
        if error is None:
            try:
                g.conn.execute(
                    "INSERT INTO Training_Material (course_name, course_id)"
                    "VALUES (%s, %s)",
                    (course_name, uuid.uuid4()),
                )
                # g.conn.commit()
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {course_name} is already registered."
            else:
                # Success, go to the login page.
                return redirect('/')

        flash(error)

    return render_template("upload_class.html")











@app.route("/update", methods=("GET", "POST"))
def update_users():
    """
Allows a CURRENTLY logged in user to update their account.
Appends desired role, skills, email, name to a given uid based on login.

INCOMPLETE

    """

    user_desired_roles = ['Data Scientist', 'Data Analyst', 'Data Engineer', 'ML Engineer']
    bool_list = ['TRUE', 'FALSE']
    deg_list = ['None', 'High School/GED', 'Associate', 'Bachelors', 'Masters', 'PHD', 'Secret Clown College']
    # current_user = g.conn.session.merge()
    if request.method == "POST":
        desired_role = request.form['desired_role']
        print(desired_role)

        email = request.form['email']
        print(email)

        full_name = request.form['full_name']
        print(full_name)

        education_level = request.form['education_level']
        print(education_level)

        # SKILLS #
        python = request.form['python']
        print(python)

        scala = request.form['scala']
        print(scala)

        java = request.form['java']
        print(java)

        excel = request.form['excel']
        print(excel)

        powerpoint = request.form['powerpoint']
        print(powerpoint)

        google_analytics = request.form['google_analytics']
        print(google_analytics)

        matlab = request.form['matlab']
        print(matlab)

        power_bi = request.form['power_bi']
        print(power_bi)

        tableau = request.form['tableau']
        print(tableau)

        aws = request.form['aws']
        print(aws)

        hive = request.form['hive']
        print(hive)

        spark = request.form['spark']
        print(spark)

        postgres = request.form['postgres']
        print(postgres)

        azure = request.form['azure']
        print(azure)

        skill_sql = request.form['skill_sql']
        print(skill_sql)
        # # SKILLS #

        error = None

        if not email:
            error = "email is required."
        elif not full_name:
            error = "full_name is required."

        if error is None:
            try:
                g.conn.execute(
                    "UPDATE users "
                    "SET "
                    "desired_role = %s, email = %s , full_name = %s , education_level  = %s ,"  # 4 key params
                    "python = %s , scala = %s , java = %s , excel = %s , powerpoint = %s,"  # first 5
                    "google_analytics = %s , matlab = %s , power_bi = %s , tableau = %s , aws = %s,"  # second 5
                    "hive = %s, spark = %s, postgres = %s, azure = %s, skill_sql = %s "  # last 5
                    "WHERE uid = %s",
                    (desired_role, email, full_name, education_level,  # 4 key parameters
                     python, scala, java, excel, powerpoint,  # first 5
                     google_analytics, matlab, power_bi, tableau, aws,
                     hive, spark, postgres, azure, skill_sql,  # last 5
                     session["uid"]  # last %s is 'where uid = session["uid"] '
                     )
                )
            except g.conn.IntegrityError:
                # The username was already taken, which caused the
                # commit to fail. Show a validation error.
                error = f"User {login} is already registered."
            else:
                # Success, go to the login page.
                return redirect(url_for("index"))

        flash(error)

    return render_template("update.html", user_desired_roles=user_desired_roles, bool_list=bool_list, deg_list=deg_list)


@app.route('/remove_user', methods=['GET', 'POST', 'DELETE'])
def remove_user():
    g.conn.execute(
          "DELETE FROM users WHERE uid =  %s", session["uid"]
    )
    return render_template("index.html")


@app.route('/remove_job', methods=['GET', 'POST', 'DELETE'])
def remove_job():
    g.conn.execute(
          "DELETE FROM datajobs_belong WHERE uid =  %s", session["uid"]
    )
    return render_template("index.html")


@app.route('/remove_ads', methods=['GET', 'POST', 'DELETE'])
def remove_ads():
    g.conn.execute(
          "DELETE ja "
          "FROM  ads"
          "INNER JOIN buys "
          "WHERE uid =  %s", session["uid"]
    )
    return render_template("index.html")


# def remove_class():
#     g.conn.execute(
#           "DELETE FROM training_material WHERE uid =  %s", session["uid"]
#     )
#     return render_template("index.html")

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
