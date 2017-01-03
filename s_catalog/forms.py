"""Forms for the application."""
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Form class for user login."""
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    """Form class for user registration."""
    name = StringField('name')
    phone = StringField("phone")
    email = StringField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    confirm_password = PasswordField('confirm password', validators=[DataRequired()])


class UpdateUserInfoForm(FlaskForm):
    """
    Form to update user name and phone. Since neither of them is required (everything is based on the primary
    email), both are optional.
    """
    phone = StringField("Contact phone:")
    name = StringField("Name:")



