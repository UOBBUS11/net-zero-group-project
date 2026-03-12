from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    is_admin = BooleanField('Login as Admin')
    submit = SubmitField('Sign In')

class LogTripForm(FlaskForm):
    distance = FloatField('Distance (km)', validators=[
        DataRequired(),
        NumberRange(min=0.1, message="Distance must be positive")
    ])
    # 選項會在 routes.py 動態載入
    mode = SelectField('Transport Mode', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Calculate & Submit')

class EditRuleForm(FlaskForm):
    base_points = IntegerField('Base Points', validators=[DataRequired()])
    points_per_km = IntegerField('Points per Km', validators=[DataRequired()])
    submit = SubmitField('Update Rule')