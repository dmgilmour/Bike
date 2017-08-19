from flask import Flask, request, abort, url_for, redirect, session, render_template, jsonify

app = Flask(__name__)

pages = ["about", "projects", "readings", "blog", "employers"]

@app.route("/")
def default():

    return render_template("head.html", pages=pages)



@app.route("/<dead_end_page>/")
def dead_end(dead_end_page):

    if dead_end_page not in pages:
        return render_template("not_found.html")

    print(dead_end_page)
    return render_template("head.html", pages=pages, cur_page=dead_end_page)
