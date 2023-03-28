from planviewpathplan import app
from planviewpathplan.helpers import apology, login_required
from planviewpathplan.pathfinder import PathFinder
import os
import sys
import sqlite3
import json
from flask import Flask, flash, redirect, render_template, request, session, jsonify
# from flask_cors import CORS
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

Session(app)

db = sqlite3.connect("planviewpathplan/users.db")
db.row_factory = sqlite3.Row
cursor = db.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
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
        userData = cursor.execute("SELECT * FROM userlogin WHERE username = :username", {"username":request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if not userData or not check_password_hash(userData["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = userData["id"]

        # Redirect user to home page
        return redirect("/")

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
    # Get user input for name
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        passwd = request.form.get("password")
        confirm = request.form.get("confirmation")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not passwd or not confirm:
            return apology("must provide password", 403)
        # Ensure passwords match
        if passwd != confirm:
            return apology("Passwords do not match",403)
        # Query database for username to ensure user does not exist
        cursor.execute("SELECT * FROM userlogin WHERE username = :username", {"username":username})
        
        if cursor.fetchone():
            return apology("User already exists", 403)

        #If we get here, we can add to database
        try:
            cursor.execute("begin")
            cursor.execute("INSERT INTO userlogin (username, hash) VALUES(?, ?)", (username, generate_password_hash(passwd)))
            cursor.execute("commit")
        except db.Error:
            print("Failed SQL update/insert!")
            cursor.execute("rollback")

        cursor.execute("SELECT * FROM userlogin WHERE username = :username", {"username":username})
        newRow = cursor.fetchone()
        print("HELLO",newRow["id"],file=sys.stderr)
        session["user_id"] = newRow["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/simulate",methods=["POST"])
def simulate():
    data = json.loads(request.form['sim_data'])
    obstacles = []
    for object in data['objects']:
        if "name" in object:
            if object["name"] == "start":
                start = (object["left"],object["top"])
            elif object["name"] == "goal":
                goal = (object["left"],object["top"])
        else:
            obstacles.append(object)

    canvasSize = json.loads(request.form['canvas_size'])
    width = canvasSize[0]
    height = canvasSize[1]
    pf = PathFinder(start,goal,(width,height),obstacles)
    orderOfVisit,finalPath = pf.findPath()
    # print("Order of visit", orderOfVisit)
    # print("Final Path", finalPath)
    return jsonify({"orderOfVisit":orderOfVisit,"finalPath":finalPath,"scale":pf.res})

# The below require user to be logged in

@app.route("/",methods=['GET','POST'])
def index():
    data = {'dataURL':None}
    return render_template("index.html",data = data)

@app.route("/save",methods=['POST'])
@login_required
def save():
    filename = request.form['save_fname']
    metaData = request.form['save_cdata']
    canvas_image = request.form['save_image']
    if filename:
        try:
            cursor.execute("begin")
            cursor.execute("INSERT INTO drawings (user_id,drawing_name,meta_data,canvas_image) VALUES(?,?,?,?)",
                (session["user_id"],filename,metaData,canvas_image))
            cursor.execute("commit")
        except db.Error:
            print("Failed SQL update/insert!")
            cursor.execute("rollback")
    return('/')
    # cur.execute("INSERT INTO files (name, data, canvas_image) VALUES (%s, %s, %s)", [filename, data, canvas_image])
    # conn.commit()
    # conn.close()

    # data = request.values.get('canvas')
    # if data:
    #     try:
    #         cursor.execute("begin")
    #         cursor.execute("INSERT INTO drawings (user_id, dataURL) VALUES(?, ?)", (session["user_id"] , data))
    #         cursor.execute("commit")
    #     except db.Error:
    #         print("Failed SQL update/insert!")
    #         cursor.execute("rollback")

    # return('/')


@app.route("/load",methods=["GET", "POST"])
@login_required
def load():
    # Read the selected canvas data from the sqlite database and return it to the user
    cursor.execute("SELECT * FROM drawings WHERE user_id = :user_id", {"user_id":session["user_id"]})
    userData = cursor.fetchall()
    # dataURL = cursor.fetchall()[-1]["dataURL"]
    if userData:
        return render_template("index.html",userData=userData)
    else:
        return('/')
        # return apology("User already exists", 403)

    