
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
algo = Algo()


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

        return render_template("home.html")
        # return render_template("home.html", bike_loc=bike_loc)

@app.route("/register", methods = ["POST"])
def registerBike():

    data = request.get_json()
    print("Register ID: ", data['id'])

@app.route("/data", methods = ["GET", "POST"])
def trackdata():

    if request.method == "GET":
        user = session['user']
        #bikes = users(find user(get bikes(get most recent location)))
        #return 

    if request.method == "POST":
        data = request.get_json()
        try:
            lat = data['lat']
            lon = data['lon']
            bikeid = data['id']

            if 'moving' in data.keys():
                moving = data['moving']
            else:
                moving = 0

            if 'battery' in data.keys():
                battery = data['battery']
            else:
                battery = -1
            time = datetime.datetime.now()
        except TypeError:
            return("406: incorrect format, accepts JSON for variables 'lat', 'lon', 'id', 'moving', 'battery'")
        if lat and lon:
            if(algo.dbWrite_location('ayyo', bikeid, lon, lat, moving, time)):
                return("200: ALERT")
            else:
                #return("200 Success!")
                return("200: ALERT")
        else:
            return("302 Invalid Request")

"""
@app.route("/alert/", methods = ["GET", "POST"])
def get_alert():
    if request.method == "GET":
        if alerto:
            data = []
            data['alert'] = alerto
            alerto = None
            return json.dumps(data)
    elif request.method == "POST":
        data = request.get_json()
        print(data['alert'])
        alerto = data['alert']
        return "200 ayyo"


def alert(string):
    alerto = string
"""

@app.route("/data/user", methods = ["GET", "POST"])
def userdata():
    if request.method == "GET":

        user = session['user']
        #loc_list = algo.get_user_history(user)

        # print (loc_list)

        data = {}
        data['lat'] = 0 #loc_list[0][1]
        data['lon'] = 0 #loc_list[0][0]

        return json.dumps(data)
        # return jsonify(loc_list)

    elif request.method == "POST":
        data = request.get_json()
        try:
            lat = data['lat']
            lon = data['lon']
            #    if data['time']:
            #    time = data['time']
            #else:
            time = datetime.datetime.now()
        except TypeError:
            return("406: incorrect format, accepts JSON for variables 'lat', 'lon', and 'time'")
        if session['user']:
            user = session['user']

            # log user data


            print(lat, lon)
                # print(request.form["lat"] + request.form["lon"])

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
