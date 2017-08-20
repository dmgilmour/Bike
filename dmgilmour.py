from flask import Flask, request, abort, url_for, redirect, session, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(25))
    name = db.Column(db.String(25))

    def __init__(ip):
        self.ip = ip
        self.name = ip

    def __init__(ip, name):
        self.ip = ip
        self.name = name


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    

class Page_Load(db.Model):
    id = db.Column(db.Integer, primary_key=True)


pages = ["about", "projects", "readings", "blog", "employers"]

@app.route("/")
def default():
    log_client_info()
    return render_template("home.html", pages=pages)



@app.route("/<dead_end_page>/")
def dead_end(dead_end_page):

    log_client_info()

    if dead_end_page not in pages:
        return render_template("not_found.html")

    print(dead_end_page)
    return render_template("head.html", pages=pages, cur_page=dead_end_page)


def log_client_info():
    print(request.remote_addr)
    print(request.environ['REMOTE_ADDR'])
