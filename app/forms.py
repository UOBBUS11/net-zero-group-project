from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    FloatField,
    SelectField
)
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, Optional


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
            NumberRange(min=0.1, message='Distance must be positive')
        ]
    )

    location = StringField(
        'Location',
        validators=[DataRequired(), Length(min=2, max=120)]
    )

    mode = SelectField('Transport Mode', coerce=int, validators=[DataRequired()])

    enters_emission_zone = BooleanField('This location is in an emission zone')
    submit = SubmitField('Log Trip')


class EditRuleForm(FlaskForm):
    mode_id = SelectField('Transport Mode', coerce=int, validators=[DataRequired()])
    emission_factor = FloatField('Emission Factor (kg CO2 per km)', validators=[DataRequired()])
    base_points = FloatField('Base Score Weight', validators=[DataRequired()])
    points_per_km = FloatField('Distance Weight', validators=[DataRequired()])
    submit = SubmitField('Update Rule')