"""Forms for the application."""
from flask_wtf import Form
from wtforms import TextField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired


class LoginForm(Form):
    """Form class for user login."""
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(Form):
        """Form class for user registration."""
        name = StringField('name')
        phone = StringField("phone")
        email = StringField('email', validators=[DataRequired()])
        password = PasswordField('password', validators=[DataRequired()])
        confirm_password = PasswordField('confirm password', validators=[DataRequired()])

