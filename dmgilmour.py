
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
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
algo = Algo()
master_secret_key = getpass('Senor Design')

ip_list = []

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.column(db.String(40))
    password = db.column(db.String(70))
    salt = db.column(db.String(40))

    def __init__(self, username, password, salt):
        self.username = username
        self.password = password
        self.salt = salt


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.String(50))
    lon = db.Column(db.String(50))
    time = db.Column(db.DateTime)
    user_ip = db.Column(db.String(50))

    def __init__(self, lat, lon, time, user_ip):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.user_ip = user_ip

@app.cli.command("initdb")
def initdb_command():
    db.drop_all()
    db.create_all()

    db.session.commit()

    """
    db.session.add(Location("lat1", "lat1", datetime.datetime.utcnow(), "ip1"))
    time.sleep(.2)
    db.session.add(Location("lat2", "lat2", datetime.datetime.utcnow(), "ip2"))
    time.sleep(.2)
    db.session.add(Location("lat3", "lat3", datetime.datetime.utcnow(), "ip3"))
    time.sleep(.2)
    db.session.add(Location("lat4", "lat4", datetime.datetime.utcnow(), "ip1"))
    time.sleep(.2)
    db.session.add(Location("lat5", "lat5", datetime.datetime.utcnow(), "ip5"))
    time.sleep(.2)
    db.session.add(Location("lat6", "lat6", datetime.datetime.utcnow(), "ip6"))

    db.session.add(User("122.122.122.122"))

    db.session.commit()

    print(Location.query.filter_by(user_ip="ip1").order_by('-id').first().lat)
"""



@app.route("/login", methods = ["GET", "POST"])
def login():
    message = ""

    if (logged_in()):
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form["user"]
        l = User.query.all()
        a = [b for b in l if b.username == username]
        print(a)
        if len(a) != 0:
            user = a[0]
        # TODO DYLAN: replace the above line with a query that sets `user = a user going by username`
            salt = user.salt # TODO DYLAN lookup the salt for the corresponding user
            combopass = (request.form["pass"] + salt + master_secret_key).encode('utf-8')
            password = bcrypt.hashpw(combopass, salt)
            if password == user.password: # TODO DYLAN change this to check the passwor
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
        print(username)
        # TODO DYlAN replace everything after 'not' with a check if username in database
        print(User.query.filter_by(username=request.form["user"]).all())
        if len(a) == 0:
            salt = bcrypt.gensalt().encode('utf-8')
            combopass = (request.form["pass"] + salt + master_secret_key).encode('utf-8')
            password = bcrypt.hashpw(combopass, salt)
            # TODO add a new user with username username, password password, and salt salt, you may need to add salt as a column but it is necessary. after than get rid of the next two lines
            db.session.add(User(username, password, salt))
            db.session.commit()
            print(db.session.query.filter_by(username=username).first())
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
    lat = data['lat']
    lon = data['lon']
    print(lat, lon, request.remote_addr)
    return redirect(url_for("home"))

@app.route("/data/user", methods = ["GET", "POST"])
def userdata():
    if request.method == "GET":
        time_boundary = datetime.datetime.now() - datetime.timedelta(minutes=1)
        l = Location.query.filter(Location.time >= time_boundary)
        l = Location.query.all()
        loc_list = [[i.lat, i.lon] for i in l]
        return jsonify(loc_list)

    else:
        data = request.get_json()
        lat = data['lat']
        lon = data['lon']
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
        if not User.query.filter_by(name=session["user"]).first():
            session.clear()
            return False 
        else:
            return True
    else:
        return False

