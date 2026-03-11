from flask_wtf import FlaskForm
<<<<<<< HEAD
from wtforms import StringField, BooleanField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Login as Admin')
    submit = SubmitField('Login')

class LogTripForm(FlaskForm):

    distance = FloatField('Distance (km)', validators=[
        DataRequired(message="Please enter a valid distance."),
        NumberRange(min=0.1, message="Distance must be greater than 0!")
    ])


    mode = SelectField('Transport Mode', coerce=int, validators=[DataRequired()])

    submit = SubmitField('Submit Trip')
=======
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class EditRuleForm(FlaskForm):
    mode_id = SelectField('Select Transport Mode', coerce=int, validators=[DataRequired()])
    base_points = IntegerField('Base Points', validators=[DataRequired()])
    points_per_km = IntegerField('Points per Km', validators=[DataRequired()])
    submit = SubmitField('Update Rule')
>>>>>>> origin/AdminPanel-byAlim
