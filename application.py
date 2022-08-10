import os
from pickle import TRUE
import re
from cs50 import SQL
from flask import  send_from_directory, Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import insert

from helpers import login_required, grading

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["grading"] = grading

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['UPLOAD_FOLDER']='static'

# Configure application to use SQLite database
db = SQL("sqlite:///students.db")
db2 = SQL("sqlite:///staff.db")


@app.route("/")
@login_required
def index():
    """Show Marks"""
    id = session["user_id"]
    nam = db.execute("SELECT * FROM   students WHERE RegNo = ?", id)
    name = nam[0]["name"].upper()
    regno = nam[0]["RegNo"]
    rows = db.execute("SELECT * FROM results WHERE regno =?", id)
    status = db.execute("SELECT status FROM results WHERE regno=?", id)
    passed = True
    if status[0]["status"] == 'F':
        passed = False
    return render_template("index.html", rows=rows, name=name, regno=regno, passed=passed, grading=grading)
    return render_template("applogy.html", error="something wrong happened", code=403)

@app.route("/staff", methods=['GET', 'POST'])
@login_required
def staff_index():
    id = session["user_id"]
    rows= db2.execute("SELECT * FROM staff WHERE sregno =?", id)
    name= rows[0]["name"]
    staff=True
    return render_template("staff_index.html", name=name, staff=staff, rows=rows)


@app.route("/new_result", methods= ['GET'])
def new_result():
    session.clear()
    return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # staff login route
        if request.form.get("staff") == "staff":
            return render_template("staff_login.html")

        # student login route
        elif request.form.get("student") == "student":
            return render_template("student_login.html")
        else: 
            return render_template("applogy.html", error='login was unseccessful', code=403)
    else:
        return render_template("login.html")

@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    #Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure Reg Number was submitted
        if not request.form.get("sregno"):
            return render_template("applogy.html", error = "Must provide Registration Number", code=403)

        # Ensure Date of Birth was submitted
        elif not request.form.get("SDOB"):
            return render_template("applogy.html", error ="Must provide Date of Birth", code=403)

        # Query database for Reg Number
        rows = db2.execute("SELECT * FROM staff WHERE sregno = ?", request.form.get("sregno"))

        # Ensure Reg number exists and Date is correct
        if len(rows) != 1 or not (rows[0]["sdob"] == request.form.get("SDOB")):
            return render_template("applogy.html", error ="Invalid Reg Number and/or Date of Birth", code=403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["sregno"]

        # Redirect user to home page
        return redirect("/staff")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("staff_login.html")



@app.route("/student_login", methods=["GET", "POST"])
def student_login():
    #Log user in

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure Reg Number was submitted
        if not request.form.get("regno"):
            return render_template("applogy.html", error = "Must provide Registration Number", code=403)

        # Ensure Date of Birth was submitted
        elif not request.form.get("DOB"):
            return render_template("applogy.html", error ="Must provide Date of Birth", code=403)

        # Query database for Reg Number
        rows = db.execute("SELECT * FROM students WHERE RegNo = ?", request.form.get("regno"))

        # Ensure Reg number exists and Date is correct
        if len(rows) != 1 or not (rows[0]["DOB"] == request.form.get("DOB")):
            return render_template("applogy.html", error ="Invalid Reg Number and/or Date of Birth", code=403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["RegNo"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("student_login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route('/<path:filename>',  methods=['GET', 'POST'])
def download(filename):
    print(app.root_path)
    full_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    print(full_path)
    #path = '/Users/MUHAMMED FAISAL KC/Desktop/Exam_Result/exma_result/students_RegNo.xlsx'
    return send_from_directory(full_path, filename)
