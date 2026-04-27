from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    FloatField,
    SelectField
)
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, Optional, Regexp


password_rules = [
    DataRequired(),
    Length(
        min=8,
        max=128,
        message="Password must be between 8 and 128 characters."
    ),
    Regexp(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$",
        message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."
    )
]


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    is_admin = BooleanField('Login as Admin')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=password_rules)
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


class EditProfileForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=3, max=64)])
    submit = SubmitField('Update Username')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=password_rules)
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')]
    )
    submit = SubmitField('Change Password')