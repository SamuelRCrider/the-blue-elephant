from flask import Flask, session, redirect, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3

from helpers import login_required

# configure app
app = Flask(__name__)

# configure session as filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# app routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        con = sqlite3.connect("blue_elephant.db")
        cur = con.cursor()

        ...

        con.close()
        return redirect("/")

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        con = sqlite3.connect("blue_elephant.db")
        cur = con.cursor()

        """implement in such a way that once a user registers, they are redirected to account page"""
        # get username, password, and confirm password
        # check all of them, flash a message if entered wrong
        # if all is good, hash the password and store it and the username in database
        # store user_id in session
        # redirect to account

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
        elif confirmation != password:
            flash("Passwords Do Not Match")
            return redirect("/register")

        new_user_pass_hash = generate_password_hash(
            password, method="pbkdf2", salt_length=16
        )

        cur.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            [username, new_user_pass_hash],
        )
        con.commit()

        row = cur.execute("SELECT * FROM users WHERE username = ?", [username])
        session["user_id"] = row[0]["id"]

        con.close()
        return redirect("/account")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        con = sqlite3.connect("blue_elephant.db")
        cur = con.cursor()

        session.clear()
        ...

        con.close()
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
        con = sqlite3.connect("blue_elephant.db")
        cur = con.cursor()

        ...

        con.close()
        return redirect("/account")
    return render_template("account.html")
