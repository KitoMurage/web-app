from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CreateWorkoutPlanForm(FlaskForm):
    name = StringField('Workout Plan Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    group_label = TextAreaField('Workout plan group', validators=[Length(max=100)])
    submit = SubmitField('Create Plan')

class AddExerciseToPlanForm(FlaskForm):
    exercise = SelectField('Select Exercise', coerce=int, validators=[DataRequired()])
    sets = IntegerField('Sets', default=3, validators=[DataRequired()])
    reps = IntegerField('Reps', default=10, validators=[DataRequired()])
    submit = SubmitField('Add Exercise')


class EditExerciseForm(FlaskForm):
    sets = IntegerField('Sets', validators=[DataRequired()])
    reps = IntegerField('Reps', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class UpdateHealthMetricsForm(FlaskForm):
    height = FloatField('Height (cm)', validators=[DataRequired()])
    current_weight = FloatField('Current Weight (kg)', validators=[DataRequired()])
    weight_goal = FloatField('Weight Goal (kg)', validators=[DataRequired()])
    weight_date = DateField('Date of Entry', validators=[DataRequired()])  # Date field
    submit = SubmitField('Update')
