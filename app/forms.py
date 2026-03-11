from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class EditRuleForm(FlaskForm):
    mode_id = SelectField('Select Transport Mode', coerce=int, validators=[DataRequired()])
    base_points = IntegerField('Base Points', validators=[DataRequired()])
    points_per_km = IntegerField('Points per Km', validators=[DataRequired()])
    submit = SubmitField('Update Rule')