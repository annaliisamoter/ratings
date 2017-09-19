"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template,
    redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # a = jsonify([1,3])
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """ Show list of users"""

    users = User.query.all()

    return render_template("user_list.html", users=users)

@app.route('/register', methods=["GET"])
def register_form():
    """ renders registration form """

    return render_template("register_form.html")

@app.route('/register', methods=["POST"])
def register_process():
    """ checks if user is registered, if not adds new user to database """

    email = request.form.get('email')
    password = request.form.get('password')

    # check if user is already in database, via email

    user_emails = db.session.query(User.email).all()

    if email in user_emails:
        error_message = "this user already exists"
        return redirect("/register", message=error_message)
    else:
        #do we need to call the set_val_user_id()???
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
