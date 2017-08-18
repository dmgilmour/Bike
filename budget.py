import json
from flask import Flask, request, abort, url_for, redirect, session, render_template, jsonify
from datetime import datetime

app = Flask(__name__)


class Category():
    name = None
    limit = None
    current = 0

    def __init__(self, name, limit):
        self.name = name
        self.limit = limit

    def serialize(self):
        return {
                'limit'     : self.limit,
                'name'      : self.name
                }


class Purchase():
    name = None
    amount = 0
    cat = None
    date = None

    def __init__(self, name, amount, cat, date):
        self.name = name
        self.amount = amount
        self.cat = cat
        self.date = date

    def serialize(self):
        return {
                'date'      : self.date,
                'cat'       : self.cat,
                'amount'    : self.amount,
                'name'      : self.name
                }


categories = list()

purchases = list()

@app.route("/")
def default():

    return render_template("budget.html")


@app.route("/cats", methods = ["GET", "POST"])
def cats():
    if request.method == "GET":
        return json.dumps([c.serialize() for c in categories])
    if request.method == "POST":
        response = request.get_json(force=True)
        categories.append(Category(response["name"], response["limit"]))
        return "OK!"

@app.route("/cats/<cat>", methods = ["DELETE"])
def delCats(cat):
    for c in categories:
        if c.name == cat:
            categories.remove(c)
            return "OK!"
            

@app.route("/purchases", methods = ["GET", "POST"])
def purs():
    if request.method == "GET":
        return json.dumps([p.serialize() for p in purchases])
    if request.method == "POST":
        response = request.get_json(force=True)
        purchases.append(Purchase(response["name"], response["amount"], response["category"], response["date"]))
        return "OK!"



