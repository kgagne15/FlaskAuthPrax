
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, StringField
from wtforms.validators import InputRequired, Email


class RegisterForm(FlaskForm):
    """Form to register for an account
    username, password, email, first_name, last_name
    """
    
    username = StringField("Username", validators=[InputRequired(message="You must enter a username")])
    password = PasswordField("Password", validators=[InputRequired(message="You must enter a password")])
    email = StringField("Email", validators=[InputRequired(message="You must enter an email"), Email()])
    first_name = StringField("First Name", validators=[InputRequired(message="You must enter a first name")])
    last_name = StringField("Last Name", validators=[InputRequired(message="You must enter a last name")])