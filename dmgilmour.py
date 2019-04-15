
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
            salt = bcrypt.gensalt()
            combopass = (request.form["pass"] + salt).encode('utf-8')
            password = bcrypt.hashpw(combopass, salt)
            
            algo.dbWrite_user(username, password, salt, 0, 0, 0)
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

    print("ayyo")
    data = request.get_json()
    print("Register ID: ", data['id'])
    algo.new_bike(session['user'], data['id'])
    return "200"

@app.route("/data", methods = ["GET", "POST"])
def trackdata():



    if request.method == "GET":
        if 'user' not in session:
            
            return("401")
        user = session['user']
        print("user: ", user)
        bikes = algo.get_bikes_by_user(user)
        print("owned bikes: ", bikes)
        loc_list = []
        for bike in bikes:
            if bike[0] != None and bike[0] > 0:
                print("this bike: ", bike[0])
                loc = algo.ayyyyyyo(bike[0])
                print(len(loc))
                if len(loc) > 0:
                    loc_list.append({'lat':loc[0][1], 'lon':loc[0][0], 'id':bike[0]})

        print(loc_list)
        return json.dumps(loc_list)
        #return json.dumps(loc_list)
        
        #bikes = users(find user(get bikes(get most recent location)))
        """
        data = {}
        data['lat'] = 40.442791
        data['lon'] = -79.955856
        """


        return json.dumps(data)

    if request.method == "POST":
        data = request.get_json()
        try:
            lat = data['lat']
            lon = data['lon']
            bikeid = data['id']
            con = data['con']

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
            print(lat, lon, bikeid, time, moving, battery, con)
            if(algo.dbWrite_location('ayyo', bikeid, lat, lon, moving, time, con)):
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

@app.route("/data/history/<bike>", methods = ["GET", "POST"])
def history(bike):

    if request.method == "GET":
        print("Getting History for Bike: ", bike)
        loc_list = []
        if bike != None:
            loc_list = algo.get_bike_history(bike[0])

        new_list = []
        last_loc = None
        top_id = 0
        for loc in loc_list:
            if loc[3] > top_id:
                top_id = loc[3]
            if last_loc == None or loc[0] != last_loc[0] or loc[1] != last_loc[1]:
                new_list.append({'lat':loc[1], 'lon':loc[0], 'id':loc[3]})
            last_loc = loc

        print(len(loc_list))
        print(len(new_list))
        print("topid", top_id)



        return json.dumps(new_list)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("login")



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
