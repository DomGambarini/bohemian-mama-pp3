import os
from flask import (
    Flask, flash, render_template,
    redirect, request,
    session, url_for)
from flask_wtf import FlaskForm, RecaptchaField
from wtforms.validators import (
    InputRequired, Length, NumberRange, URL, DataRequired)
from wtforms import (
    StringField, PasswordField, RadioField, IntegerField,
    SubmitField, SelectField, TextAreaField, DateField)
from datetime import date
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_NAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
app.config['RECAPTCHA_PUBLIC_KEY'] = os.environ.get("RECAPTCHA_PUBLIC_KEY")
app.config['RECAPTCHA_PRIVATE_KEY'] = os.environ.get("RECAPTCHA_PRIVATE_KEY")


mongo = PyMongo(app)


class addRecipe(FlaskForm):
    recipe_name = StringField(
        'Recipe Name', validators=[InputRequired(), Length(min=4, max=40)])
    cook_time = IntegerField(
        'Cook/Prep Time in Minutes', validators=[
            InputRequired(), NumberRange(min=1, max=300, message="Please enter a number between 1 and 300.")])
    serves = IntegerField(
        'How Many Does it Serve', validators=[
            InputRequired(), NumberRange(min=1, max=20)])
    season = SelectField('Select Season', choices=[(
        '1', 'Winter'), ('2', 'Spring'), ('3', 'Summer'), ('4', 'Autumn')])
    ingredients = TextAreaField('Ingredients', validators=[
        InputRequired(), Length(min=30, max=300)])
    method = TextAreaField('Method', validators=[
        InputRequired(), Length(min=30, max=500)])
    submit = SubmitField('Add Recipe')
    todays_date = DateField(
        'Todays Date', format='%y-%m-%d', default=date.today(), validators=[])
    recaptcha = RecaptchaField()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = addRecipe()
    seasons = mongo.db.seasons.find().sort("season_name", 1)
    if form.validate_on_submit():
        return '<h2>You have successfully added your {} recipe!'.format(
            form.recipe_Name.data, seasons=seasons)
    return render_template('add-recipe.html', form=form)


@app.route('/recipes', methods=["GET", "POST"])
def recipe():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/signin", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/signout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host=os.environ.get("I.P", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
