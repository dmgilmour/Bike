from flask import Flask, request, abort, url_for, redirect, session, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def default():

    return render_template("home.html")

