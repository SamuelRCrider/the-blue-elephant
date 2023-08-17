from flask import Flask, session, redirect, render_template, request, flash
from flask_session import Session
import sqlite3

from helpers import login_required

# configure app
app = Flask(__name__)

# configure session as filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure sqlite3 database
con = sqlite3.connect("blue_elephant.db")
cur = con.cursor()


# app routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        ...
        return redirect("/")
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # implement in such a way that once a user registers, they are redirected to account page
        ...
        return redirect("/account")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        ...
        return redirect("/account")
    return render_template("login.html")


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        ...
        return redirect("/account")
    return render_template("account.html")
