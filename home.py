
''' flask app with mongo '''

import os
import json
import sys
import datetime
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.column(db.String(30))
    loc_list = db.relationship("Location", backref="user", lazy="dynamic")

    def __init__(self, ip):
        self.ip = ip


class Bike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loc_list = db.relationship("Location", backref="bike", lazy="dynamic")

    def __init__(self, ip):
        self.ip = ip

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.String(30))
    lon = db.Column(db.String(30))
    time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, lat, lon, time):
        self.lat = lat
        self.lon = lon
        self.time = time

@app.cli.command("initdb")
def initdb_command():
    db.drop_all()
    db.create_all()

    db.session.commit()



@app.route("/", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form["lat"] + request.form["lon"])
        sys.stderr.write(request.form["lat"] + request.form["lon"])

    return render_template("home.html")
    # return render_template("home.html", bike_loc=bike_loc)

@app.route("/data", methods = ["POST"])
def trackdata():
    data = request.get_json()
    lat = data['lat']
    lon = data['lon']
    print(lat, lon)
    return redirect(url_for("home"))

@app.route("/data/user", methods = ["POST"])
def userdata():
    data = request.get_json()
    lat = data['lat']
    lon = data['lon']
    print(lat, lon)
        # print(request.form["lat"] + request.form["lon"])
    return redirect(url_for("home"))
