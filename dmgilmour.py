
''' flask app with mongo '''

import os
import json
import sys
import time
import datetime
import bcrypt
from getpass import getpass
from appAlgoTime import Algo
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
algo = Algo()

"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.column(db.String(30))
    loc_list = db.relationship("Location", backref="user", lazy="dynamic")

    def __init__(self, ip):
        self.ip = ip
"""

"""
class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loc_list = db.relationship("Location", backref="bike", lazy="dynamic")

    def __init__(self, ip):
        self.ip = ip
"""



@app.route("/login", methods = ["GET", "POST"])
def login():
    message = ""

    if (logged_in()):
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form["user"]
        user = algo.get_user(username)
        if user != None:
            username = user[0]
            salt = user[2].encode('utf-8')
            print(salt)
            combopass = (request.form["pass"] + salt).encode('utf-8')
            password = bcrypt.hashpw(combopass, salt)
            if password == user[1]:
                session["user"] = username
                return redirect(url_for("home"))
            else:
                message = "Invalid credentials"
        else:
            message = "Invalid credentials"

    return render_template("login.html", message=message)

@app.route("/signup/", methods = ["GET", "POST"])
def signup():
    message = ""

    if (logged_in()):
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["user"].encode('utf-8')
        if algo.get_user(username) == None:
            salt = bcrypt.gensalt().encode('utf-8')
            combopass = (request.form["pass"] + salt).encode('utf-8')
            password = bcrypt.hashpw(combopass, salt)
            algo.dbWrite_user(username, password, salt)
            message = "New user added"
        else:
            message = "Username already in use"

    return render_template("signup.html", message=message)

@app.route("/", methods = ["GET", "POST"])
def home():

    if (not(logged_in())):
        return redirect(url_for("login"))
    else:
    
        #time_boundary = datetime.datetime.now() - datetime.timedelta(minutes=1)
        #l = Location.query.filter(Location.time >= time_boundary)
        l = Location.query.all()
        loc_list = [[i.lat, i.lon] for i in l]
        print(loc_list)

        return render_template("home.html")
        # return render_template("home.html", bike_loc=bike_loc)

@app.route("/data", methods = ["POST"])
def trackdata():
    data = request.get_json()
    try:
        lat = data['lat']
        lon = data['lon']
        bike = data['id']
        if data['time']:
            time = data['time']
        else:
            time = datetime.datetime.now()
    except TypeError:
        return("406: incorrect format, accepts JSON for variables 'lat', 'lon', and 'id'")
    if lat and lon:
        print(lat, lon, request.remote_addr)
        return("200 Success!")
    else:
        return("302 Invalid Request")

@app.route("/data/user", methods = ["GET", "POST"])
def userdata():
    if request.method == "GET":
        time_boundary = datetime.datetime.now() - datetime.timedelta(minutes=1)
        l = Location.query.filter(Location.time >= time_boundary)
        l = Location.query.all()
        loc_list = [[i.lat, i.lon] for i in l]
        return jsonify(loc_list)

    elif request.method == "POST":
        data = request.get_json()
        try:
            lat = data['lat']
            lon = data['lon']
            if data['time']:
                time = data['time']
            else:
                time = datetime.datetime.now()
        except TypeError:
            return("406: incorrect format, accepts JSON for variables 'lat', 'lon', and 'time'")
        if session['user']:
            user = session['user']

            # log user data


            ip = request.remote_addr
            print(lat, lon, ip)
                # print(request.form["lat"] + request.form["lon"])
            last_loc = Location.query.filter(Location.user_ip == ip).first()
            if last_loc != None:
                db.session.delete(last_loc)
            db.session.add(Location(lat, lon, datetime.datetime.utcnow(), ip))
            db.session.commit()

            print(Location.query.order_by('-id').first().lat)

        """
        ips = [u.ip for u in User.query.all()]
        print(ips)

        if not (ip in ips):
            print("new ip!")
            db.session.add(User(ip))
            db.session.commit()
        else:
            print("old ip")

        ips2 = [u.ip for u in User.query.all()]
        print(ips2)
        """
        
        return redirect(url_for("home"))


@app.route("/sw/", methods=["POST"])
def sw():
    data=request.get_json()
    print(data['sw'])


@app.route("/sw.js")
def swjs():
    print("visited")
    return app.send_static_file('sw.js')

def logged_in():
    if "user" in session:
        if not algo.get_user(session["user"]):
            session.clear()
            return False 
        else:
            return True
    else:
        return False



app.secret_key = "Senor Design"
