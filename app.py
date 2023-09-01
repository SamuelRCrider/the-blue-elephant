from flask import Flask, session, redirect, render_template, request, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import urllib.request, json
import sqlite3
from secret_keys import UNSPLASH_API_KEY

from helpers import login_required, logged_in

# configure app
app = Flask(__name__)

# configure session as filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure database
DATABASE = "blue_elephant.db"

# configure api
unsplash_api_url = "https://api.unsplash.com/"


def query_db(query, args=(), one=False):
    def make_dicts(cursor, row):
        return dict(
            (cursor.description[idx][0], value) for idx, value in enumerate(row)
        )

    db = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts

    cur = db.cursor()
    cur.execute(query, args)
    if "INSERT" or "DELETE" or "UPDATE" in query:
        db.commit()

    res = cur.fetchall()
    db.close()
    return (res[0] if res else None) if one else res


# app routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # code to hit api and redirect to a single page of the searched images (10 images)
        query = request.form.get("search")
        if not query:
            flash("Must Enter Query")
            return redirect("/")

        url = f"{unsplash_api_url}search/photos?client_id={UNSPLASH_API_KEY}&query={query}"
        response = urllib.request.urlopen(url)
        dict = json.load(response)

        return render_template("index.html", dict=dict)
    else:
        # code to hit api and return 10 random images (single page)
        ...

        if logged_in():
            return render_template("index.html", log=True)
        return render_template("index.html", log=False)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        """implement in such a way that once a user registers, they are redirected to account page"""
        # get username, password, and confirm password
        # check all of them, flash a message if entered wrong
        # if all is good, hash the password and store it and the username in database
        # store user_id in session
        # redirect to account
        session.clear()

        username = request.form.get("username")
        if not username:
            flash("Must Enter a Username")
            return redirect("/register")
        elif not username.isalpha():
            flash("Username Must Only Contain Characters")
            return redirect("/register")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            flash("Must Enter a Password")
            return redirect("/register")
        elif not confirmation:
            flash("Must Confirm Password")
            return redirect("/register")
        elif not password.isalnum():
            flash("Password Must Only Contain Characters and Numbers")
            return redirect("/register")
        elif len(password) < 8:
            flash("Password Must Be At Least 8 Characters")
            return redirect("/register")
        elif confirmation != password:
            flash("Passwords Do Not Match")
            return redirect("/register")

        new_user_pass_hash = generate_password_hash(
            password, method="pbkdf2", salt_length=16
        )

        query_db(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            [username, new_user_pass_hash],
        )

        row = query_db("SELECT * FROM users WHERE username = ?", [username], one=True)

        session["user_id"] = row["id"]

        return redirect("/account")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.clear()
        # get username and password
        # check username and password against database
        # if good, log in user (redirect to account page) and set session to user_id
        username = request.form.get("username")
        if not username:
            flash("Please Enter Username")
            return redirect("/login")
        try:
            data_check = query_db(
                "SELECT * FROM users WHERE username = ?", [username], one=True
            )
        except TypeError:
            flash("Username Not Valid")
            return redirect("/login")

        password = request.form.get("password")
        if not password:
            flash("Please Enter Password")
            return redirect("/login")
        try:
            check_password_hash(data_check["hash"], password)
        except TypeError:
            flash("Password Not Valid")
            return redirect("/login")

        session["user_id"] = data_check["id"]

        return redirect("/account")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        # get email and confirmation
        # make sure it is a valid email and it matches confirmation
        # make sure it doesn't already exist in database
        # if good, get frequency and put it in database
        email = request.form.get("email")
        if not email:
            flash("Please Enter Email")
            return redirect("/account")

        confirm_email = request.form.get("confirm_email")
        if not confirm_email:
            flash("Must Confirm Email")
            return redirect("/account")

        if email != confirm_email:
            flash("Emails Entered Do Not Match")
            return redirect("/account")

        frequency = request.form.get("frequency")
        if not frequency:
            flash("Must Select Frequency")
            return redirect("/account")

        frequency = int(frequency)

        try:
            query_db(
                "INSERT INTO emails (user_id, address, frequency) VALUES (?, ?, ?)",
                [session["user_id"], email, frequency],
            )
            flash("Success! Welcome to the Email List!")
        except Exception:
            flash("Unable To Join Email List At This Time")
            return redirect("/account")

        return redirect("/account")
    else:
        if logged_in():
            return render_template("account.html", log=True)
        return render_template("account.html", log=False)


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "POST":
        ...
        flash("Message Sent!")
        return redirect("/account")
    else:
        if logged_in():
            return render_template("contact.html", log=True)
        return render_template("index.html", log=False)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    if request.method == "POST":
        ...
        flash("Email Frequency Updated!")
        return redirect("/account")
    else:
        if logged_in():
            return render_template("update.html", log=True)
        return render_template("index.html", log=False)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        ...
        flash("Account Deleted!")
        return redirect("/index")
    else:
        if logged_in():
            return render_template("delete.html", log=True)
        return render_template("index.html", log=False)
