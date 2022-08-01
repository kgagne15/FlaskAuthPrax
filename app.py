from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
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
    if 'username' not in session:
        flash("Please login first")
        return redirect('/login')
    return render_template('secrets.html')

@app.route('/users/<username>')
def user_info(username):
    """Show info about user after login"""
    if 'username' not in session or session['username'] != username:
        flash("Please login first")
        return redirect('/login')
    user = User.query.get_or_404(username)
    feedback = user.feedback
    return render_template('user_info.html', user=user, feedback=feedback)

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
       
        return redirect(f'/users/{new_user.username}')
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
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!")
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def feedback_form(username):
    """Add new feedback from user account"""
    form = FeedbackForm()

    if 'username' not in session:
        flash("Please login first")
        return redirect('/login')
    if form.validate_on_submit() and session['username'] == username:
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f'users/{username}')
    else: 
        return render_template('feedback_form.html', username=username, form=form)
    
@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_feedback(id):
    """Update feedback"""
    form = FeedbackForm()
    feedback = Feedback.query.get(id)
    username = feedback.username
    if 'username' not in session:
        flash("Please login first")
        return redirect('/login')
    if form.validate_on_submit():
        if session['username'] == username:
            feedback = Feedback.query.get(id)
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            return redirect(f'users/{username}')
        else: 
            flash("You can't access this post")
            return redirect(f'/login')
    else: 
        if session['username'] == username: 
            return render_template('feedback_update_form.html', username=username, form=form, id=id)
        else:
            flash("Login as the post owner")
            return redirect('/login')

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    """Delete feedback"""
    feedback = Feedback.query.get(id)
    username = feedback.username
    if 'username' not in session:
        flash("Please login first")
        return redirect('/login')

    if session['username'] == username:
        feedback = Feedback.query.get(id)
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'users/{username}')
    else: 
        flash("Login as the post owner")
        return redirect('/login')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user_account(username):
    """delete user account"""
    if 'username' not in session or session['username'] != username: 
        flash("Login as user")
        return redirect('/login')
    
    user = User.query.get(username)
    feedback = user.feedback

    for f in feedback: 
        db.session.delete(f)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/')