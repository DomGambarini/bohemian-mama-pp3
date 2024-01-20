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
    SubmitField, SelectField, TextAreaField, DateField, URLField)
from flask_pymongo import PyMongo
from datetime import date
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
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'


mongo = PyMongo(app)


class addRecipe(FlaskForm):
    season = SelectField('Select Season', choices=[(
        'Winter'), ('Spring'), ('Summer'), ('Autumn')])
    recipe_name = StringField(
        'Recipe Name', validators=[InputRequired(), Length(min=4, max=40)])
    cook_time = IntegerField(
        'Cook/Prep Time in Minutes', validators=[InputRequired(), NumberRange(
            min=1, max=300, message="Please enter a number between 1 and 300.")])
    serves = IntegerField(
        'How Many Does it Serve', validators=[
            InputRequired(), NumberRange(min=1, max=20)])
    ingredients = TextAreaField('Ingredients', validators=[
        InputRequired(), Length(min=30, max=300)])
    method = TextAreaField('Method', validators=[
        InputRequired(), Length(min=30, max=500)])
    image = URLField('Add URL Image Here', validators=[InputRequired()])
    date = DateField(format='%Y-%m-%d')
    submit = SubmitField('Add Recipe')


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = addRecipe()
    if form.validate_on_submit():
        recipe = {
            'image': request.form.get('image'),
            "season": request.form.get("season"),
            "recipe_name": request.form.get("recipe_name"),
            "cook_time": request.form.get("cook_time"),
            "serves": request.form.get("serves"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "date": request.form.get("date")
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe has been uploaded!")
        return redirect(url_for("recipe"))

    season = mongo.db.season.find().sort("season_name", 1)
    return render_template('add-recipe.html', season=season, form=form)


@app.route('/recipes', methods=["GET"])
def recipe():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    form = addRecipe()
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    season = mongo.db.season.find().sort("season_name", 1)
    return render_template("edit-recipe.html", recipe=recipe, form=form)


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
    if session["user"]:
        return redirect(url_for("login"))
    # grab the session user's username from db
    user = mongo.db.users.find_one_or_404(
        {"username": username})
    return render_template("profile.html", username=username)


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
