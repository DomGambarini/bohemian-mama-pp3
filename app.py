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
from datetime import datetime
from bson.objectid import ObjectId
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)
current_time = datetime.now()
formatted_date = current_time.strftime("%d/%m/%Y")


class addRecipe(FlaskForm):
    season_name = SelectField(
        u'Select a Season',
        choices=[
            ('', 'Choose your option'),
            ('Winter', 'Winter'),
            ('Spring', 'Spring'),
            ('Summer', 'Summer'),
            ('Autumn', 'Autumn')],
        validators=[InputRequired()],
        default=''
    )
    recipe_name = StringField(
        'Recipe Name', validators=[InputRequired(), Length(min=4, max=40)])
    cook_time = IntegerField(
        'Cook/Prep Time in Minutes', validators=[InputRequired(), NumberRange(
            min=1, max=300, message="Please enter a number between 1 and 300."
        )])
    serves = IntegerField(
        'How Many Does it Serve', validators=[
            InputRequired(), NumberRange(min=1, max=20)])
    ingredients = TextAreaField('Ingredients', validators=[
        InputRequired(), Length(min=30, max=1000)])
    method = TextAreaField('Method', validators=[
        InputRequired(), Length(min=30, max=5000)])
    image = URLField('Add URL Image Here', validators=[InputRequired()])
    submit = SubmitField('Add Recipe')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.bm_users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.bm_users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.bm_users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"],
               request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("signin"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("signin"))

    return render_template("signin.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if "user" not in session:
        return redirect(url_for('signin'))
    # grab the session user's username from db
    username = mongo.db.bm_users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("signin"))


@app.route("/signout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("signin"))


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if "user" not in session:
        return redirect(url_for('signin'))
    form = addRecipe()

    if form.validate_on_submit():
        ingredients = request.form.get("ingredients").split("\n")
        recipe = {
            'image': request.form.get('image'),
            "season_name": request.form.get("season_name"),
            "recipe_name": request.form.get("recipe_name"),
            "cook_time": request.form.get("cook_time"),
            "serves": request.form.get("serves"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"],
            "posted": formatted_date
        }

        mongo.db.recipes.insert_one(recipe)
        flash("Your recipe has been uploaded!")
        return redirect(url_for("recipe"))

    seasons = mongo.db.seasons.find().sort("season_name", 1)
    return render_template('add-recipe.html', seasons=seasons, form=form)


@app.route("/test/<recipe_id>", methods=["GET", "POST"])
def test(recipe_id):

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    form = addRecipe(request.form, data=recipe)
    print(recipe)
    return render_template('edit-recipe copy.html', form=form, recipe=recipe)


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if "user" not in session:
        return redirect(url_for('signin'))
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    form = addRecipe(request.form, data=recipe)
    if form.validate_on_submit():
        submit_recipe = {
            'image': request.form.get('image'),
            "season_name": request.form.get("season_name"),
            "recipe_name": request.form.get("recipe_name"),
            "cook_time": request.form.get("cook_time"),
            "serves": request.form.get("serves"),
            "ingredients": request.form.get("ingredients"),
            "method": request.form.get("method"),
            "created_by": session["user"],
            "posted": formatted_date
        }
        update_recipe = {"$set": submit_recipe}
        mongo.db.recipes.update_one({"_id": ObjectId(
            recipe_id)}, update_recipe)
        flash("Recipe successfully updated!")
        seasons = mongo.db.seasons.find().sort("season_name", 1)
        return redirect(url_for(
            "recipe", seasons=seasons, recipe_id=recipe_id))

    return render_template(
        "edit-recipe.html", form=form, recipe=recipe)


@app.route('/recipes/', methods=["GET"])
def recipe():
    recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


@app.route('/view_recipe/<recipe_id>', methods=["GET"])
def view_recipe(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    form = addRecipe(request.form, data=recipe)
    return render_template("view_recipe.html", recipe=recipe)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    if "user" not in session:
        return redirect(url_for('signin'))
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe Deleted")
    return redirect(url_for("recipe", recipe_id=recipe_id))


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(
        host=os.environ.get("I.P", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
