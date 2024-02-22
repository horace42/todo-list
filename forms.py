"""
FlaskForm forms definitions
"""
from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired


class AddList(FlaskForm):
    name = StringField("New list name:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AddTask(FlaskForm):
    name = StringField("New task name:", validators=[DataRequired()])
    deadline = DateField("Deadline",
                         default=datetime.today,
                         validators=[DataRequired()])
    submit = SubmitField("Submit")
