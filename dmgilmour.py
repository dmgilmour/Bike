
''' flask app with mongo '''

import os
import json
import sys
import time
import datetime
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.column(db.String(30))

    def __init__(self, ip):
        self.ip = ip
        """


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


@app.route("/", methods = ["GET", "POST"])
def home():
    
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
