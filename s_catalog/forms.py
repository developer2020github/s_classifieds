"""Forms for the bull application."""
from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    """Form class for user login."""
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


