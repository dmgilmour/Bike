
''' flask app with mongo '''

import os
import json
import sys
import datetime
from flask import Flask, request, abort, url_for, redirect, session, render_template, flash
from flask import render_template

app = Flask(__name__)

@app.route("/", methods = ["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form["lat"] + request.form["lon"])
        sys.stderr.write(request.form["lat"] + request.form["lon"])

    return render_template("home.html")

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
