from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "321cba"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)


toolbar = DebugToolbarExtension(app)

#****************
#Routes logic
#****************

@app.route('/')
def root_route():
    """Root Route that will redirect to the Register page"""
    return redirect('/register')

@app.route('/secret')
def secret_route():
    """Route for only registered users"""
    return render_template('secrets.html')

@app.route('/register', methods=["GET", "POST"])
def register_form():
    """Displays/Submits the registration form for users"""
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username or email taken.  Please pick another')
            return render_template('register.html', form=form)
        session['username'] = new_user.username
        flash("Welcome, you've successfully registered!")
        return redirect('/secret')
    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_form():
    """Displays/Submits login form for users"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome Back, {user.username}!')
            return redirect('/secret')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)