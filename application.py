import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime
from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") is None:
        showbutton = False
        return render_template("index.html", showbutton=showbutton)
    else:
        showbutton = True
        usern = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        user = usern[0]["username"]
        return render_template("index.html", user=user, showbutton=showbutton)


@app.route("/about")
def about():
    if session.get("user_id") is None:
        showbutton = False
        return render_template("about.html", showbutton=showbutton)
    else:
        showbutton = True
        usern = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        user = usern[0]["username"]
        return render_template("about.html", user=user, showbutton=showbutton)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id, but maintain flashed message if present

    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form.get("username")
        password = request.form.get("password")
        cpassword = request.form.get("confirmation")

        if cpassword != password:
            flash("Error")
        # Ensure username was submitted
        elif not request.form.get("username"):
            flash("Error")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Error")

        result = db.execute("SELECT id FROM users WHERE username = ?", name)

        if result:
            flash("Error")

        # Stores username
        db.execute("INSERT INTO users (username,password,hash) VALUES (?,?,?)", name, password, generate_password_hash(password))

        return render_template("login.html")


@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "GET":
        remind = db.execute("SELECT ID, reminder FROM reminders WHERE userID = ?", session["user_id"])
        agendas = db.execute("SELECT ID, Event, date FROM agenda WHERE userID = ?", session["user_id"])
        return render_template("main.html", remind=remind, agendas=agendas)
    else:

        remind = db.execute("SELECT ID, reminder FROM reminders WHERE userID = ?", session["user_id"])
        agendas = db.execute("SELECT ID, Event, date FROM agenda WHERE userID = ?", session["user_id"])
        return render_template("main.html", remind=remind, agendas=agendas)


@app.route("/agenda", methods=["GET", "POST"])
@login_required
def agenda():
    if request.method == "GET":
        return render_template("agenda.html")
    else:
        descr = request.form.get("description")
        dateagenda = request.form.get("date")

        if not request.form.get("description"):
            flash("Error")
        if not request.form.get("date"):
            flash("Error")

        db.execute("INSERT INTO agenda (userID,Event,date) VALUES (?,?,?)", session["user_id"], descr, dateagenda)
        flash("Successfully added!")
        return redirect("/main")


@app.route("/reminder", methods=["GET", "POST"])
@login_required
def reminder():
    if request.method == "GET":
        return render_template("reminder.html")
    else:
        descr = request.form.get("description")
        if not request.form.get("description"):
            flash("Error")

        db.execute("INSERT INTO reminders (userID,reminder) VALUES (?,?)", session["user_id"], descr)
        flash("Successfully added!")
        return redirect("/main")


@app.route("/deleteone", methods=["POST"])
def deleteone():
    theid1 = request.form.get("id")
    db.execute("DELETE FROM reminders WHERE ID = ?", theid1)
    return redirect("/main")


@app.route("/deletetwo", methods=["POST"])
def deletetwo():
    theid2 = request.form.get("id")
    db.execute("DELETE FROM agenda WHERE ID = ?", theid2)
    return redirect("/main")