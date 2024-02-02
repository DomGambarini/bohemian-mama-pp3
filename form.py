from flask_wtf import FlaskForm, RecaptchaField
from wtforms.validators import (
    InputRequired, Length, NumberRange, URL, DataRequired)
from wtforms import (
    StringField, PasswordField, RadioField, IntegerField,
    SubmitField, SelectField, TextAreaField, DateField, URLField)


class RecipeForm(FlaskForm):
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
