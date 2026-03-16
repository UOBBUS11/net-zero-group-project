from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=128)])
    is_admin = BooleanField('Login as Admin')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=128)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )
    submit = SubmitField('Create Account')


class LogTripForm(FlaskForm):
    distance = FloatField(
        'Distance (km)',
        validators=[
            DataRequired(),
            NumberRange(min=0.1, message="Distance must be positive")
        ]
    )
    mode = SelectField('Transport Mode', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Calculate & Submit')


class EditRuleForm(FlaskForm):
    base_points = IntegerField('Base Points', validators=[DataRequired()])
    points_per_km = IntegerField('Points per Km', validators=[DataRequired()])
    submit = SubmitField('Update Rule')