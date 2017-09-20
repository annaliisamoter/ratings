"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template,
    redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie

from datetime import date


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

@app.route('/user', methods=["GET"])
def show_user():
    """ Display user info"""

    user = request.args.get('user')

    u = User.query.options(db.joinedload('ratings')).filter(User.user_id == user)
    u = u[0]
    user_age = u.age
    user_zipcode = u.zipcode
    user_ratings = u.ratings

    return render_template('user_info.html', user_id=user, user_age=user_age,
        user_zipcode=user_zipcode, user_ratings=user_ratings)

@app.route('/movies')
def movie_list():
    """ show list of movies"""

    movies = Movie.query.order_by('title').all()

    return render_template('movie_list.html', movies=movies)

@app.route('/movie', methods=["GET"])
def show_movie():
    """ show details about a movie, given movie_id"""

    movie_id = request.args.get('movie')

    m = Movie.query.options(db.joinedload('ratings')).filter(Movie.movie_id == movie_id)

    m = m[0]
    ratings = m.ratings
    released_at = m.released_at.date()

    return render_template('movie_info.html', movie=m, ratings=ratings, released_at=released_at)


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

    q = db.session.query(User).filter(User.email == email).all()

    if q:
        print "user already exists"
        flash("User already exists")
        return redirect('/login')

    else:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        print "new user has been added to the database"
        flash("Welcome!")
        return redirect("/")


@app.route('/login', methods=["GET"])
def login_display():
    """ return login page """

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_process():
    """ validate email & pass & stores in session """
    email = request.form.get("email")
    password = request.form.get("password")

    q = db.session.query(User).filter(User.email == email).first()

    if q and q.password == password:
        print q, q.password
        session['user_id'] = q.user_id
        flash("You are logged in!")
        print "login success"
        return redirect('/user?user={}'.format(q.user_id))

    else:
        flash("Login failed, please try again")
        print "login failed"
        return redirect('/login')


@app.route('/logout')
def logout_process():
    """logs user out of session"""

    session['user_id'] = None
    flash("You've been logged out.  Goodbye!")
    return redirect('/')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = False
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')
