import os
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/seasonalrecipes.html")
def seasonalrecipes():
    return render_template("seasonalrecipes.html")


@app.route("/login.html")
def login():
    return render_template("login.html")


@app.route("/register.html")
def register():
    return render_template("register.html")
 

if __name__ == "__main__":
    app.run(
        host=os.environ.get("I.P", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)