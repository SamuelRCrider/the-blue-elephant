from flask import Flask, session, redirect, render_template, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import urllib.request, json
import sqlite3
import smtplib
import ssl
from email.message import EmailMessage
from secret_keys import UNSPLASH_API_KEY, MAIL_PASSWORD
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from helpers import (
    login_required,
    logged_in,
    transform_post_rawData,
    transform_get_rawData,
    transform_login_rawData,
)

# configure app
app = Flask(__name__)


# configure session as filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure api
unsplash_api_url = "https://api.unsplash.com/"

# configure database
DATABASE = "blue_elephant.db"


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


# handle sending emails here
def send_mail():
    users = query_db("SELECT * FROM emails")
    url = f"{unsplash_api_url}photos/random?client_id={UNSPLASH_API_KEY}&query=cute+animals&count=9"
    response = urllib.request.urlopen(url)
    dict = json.load(response)
    urls = transform_get_rawData(dict)
    # Define email sender and receiver
    for user in users:
        email_sender = "the.official.blue.elephant@gmail.com"
        email_password = MAIL_PASSWORD
        email_receiver = user["address"]

        # Set the subject and body of the email
        subject = "Your Daily Dose Of Cuteness"
        body = f"{urls}"

        em = EmailMessage()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        em.set_content(body)

        # Add SSL (layer of security)
        context = ssl.create_default_context()

        # Log in and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())


scheduler = BackgroundScheduler()
scheduler.add_job(send_mail, "interval", minutes=1440)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


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

        url_Data = transform_post_rawData(dict)

        return render_template("index.html", url_Data=url_Data)
    else:
        # code to hit api and return 10 random images (single page)
        url = f"{unsplash_api_url}photos/random?client_id={UNSPLASH_API_KEY}&query=cute+animals&count=9"
        response = urllib.request.urlopen(url)
        dict = json.load(response)

        url_Data = transform_get_rawData(dict)

        if logged_in():
            return render_template("index.html", log=True, url_Data=url_Data)
        return render_template("index.html", log=False, url_Data=url_Data)


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

    else:
        url = f"{unsplash_api_url}photos/random?client_id={UNSPLASH_API_KEY}&query=cute+animals"
        response = urllib.request.urlopen(url)
        dict = json.load(response)

        url_Data = transform_login_rawData(dict)

        return render_template("register.html", url_Data=url_Data)


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

    else:
        url = f"{unsplash_api_url}photos/random?client_id={UNSPLASH_API_KEY}&query=cute+animals"
        response = urllib.request.urlopen(url)
        dict = json.load(response)

        url_Data = transform_login_rawData(dict)

        return render_template("login.html", url_Data=url_Data)


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

        try:
            query_db(
                "INSERT INTO emails (user_id, address) VALUES (?, ?)",
                [session["user_id"], email],
            )
            flash("Success! Welcome to the Email List!")
        except Exception:
            flash("Unable To Join Email List At This Time")
            return redirect("/account")

        return redirect("/account")
    else:
        if logged_in():
            temp = query_db(
                "SELECT address FROM emails WHERE user_id = ?", [session["user_id"]]
            )
            if not temp:
                return render_template("account.html", log=True, temp=False)
            else:
                return render_template("account.html", log=True, temp=True)
        return render_template("account.html", log=False)


@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if logged_in():
        return render_template("contact.html", log=True)
    return render_template("index.html", log=False)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash("Please Enter Username")
            return redirect("/delete")
        try:
            data_check = query_db(
                "SELECT * FROM users WHERE username = ?", [username], one=True
            )
        except TypeError:
            flash("Username Not Valid")
            return redirect("/delete")

        password = request.form.get("password")
        if not password:
            flash("Please Enter Password")
            return redirect("/delete")
        try:
            check_password_hash(data_check["hash"], password)
        except TypeError:
            flash("Password Not Valid")
            return redirect("/delete")

        if session["user_id"] == data_check["id"]:
            try:
                query_db("DELETE FROM users WHERE id = ?", [data_check["id"]])
            except Exception:
                flash("Account Cannot Be Deleted At This Time, Please Try Again Later")
                return redirect("/account")

            check_email = query_db(
                "SELECT * FROM emails WHERE user_id = ?", [data_check["id"]]
            )
            if check_email:
                try:
                    query_db("DELETE FROM emails WHERE user_id = ?", [data_check["id"]])
                except Exception:
                    flash(
                        "Account Cannot Be Deleted At This Time, Please Try Again Later"
                    )
                    return redirect("/account")

        else:
            flash("Account Cannot Be Deleted At This Time, Please Try Again Later")
            return redirect("/account")

        flash("Account Deleted!")
        session.clear()
        return redirect("/")
    else:
        if logged_in():
            return render_template("delete.html", log=True)
        return render_template("index.html", log=False)
