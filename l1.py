from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_login import LoginManager
from flask_login import current_user, login_required, login_manager


# from flask_wtf.csrf import CSRFProtect
from sqlalchemy import create_engine

e = create_engine("mysql://scott:tiger@localhost/test", pool_recycle=3600)

app = Flask(__name__)
# Set a secret key for CSRF protection
app.config['SECRET_KEY'] = 'your-secret-key'
# csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/user'
# engine = create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
# from your_app import db

class User(UserMixin, db.Model):
    # __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Signup(db.Model):
    # id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    msg = db.Column(db.String(120), nullable=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=False)
    username = db.Column(db.String(100), nullable=False)
    carname = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, id, username, carname, date):
        self.id = id
        self.username = username
        self.carname = carname
        self.date = date

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    if request.method == 'POST':
        selected_city = request.form.get('city')
        return redirect(f'/view_car/{selected_city}')
    return render_template('paras.html')
#book car function
# @app.route('/book_car', methods=['POST'])
# def book_car():
#     username = request.form['username']
#     # password = request.form['password']

#     # Check if the username and password exist in the 'signup' table
#     user = Signup.query.filter_by(username=username).first()

#     if user:
#         return 'Car booked successfully.'
#     else:
#         return 'Invalid username or password.'
#         return redirect(url_for('signup'))


@app.route('/book_car', methods=['POST'])
def book_car():
    # Get the form data
    username = request.form['username']

    

    # Check if the username exists in the 'signup' table
    user = Signup.query.filter_by(username=username).first()

    booking = None
    if user:
        # If the username exists, redirect to the new.html page
         ###########################
        carname = request.form['carname']
        booking_id = int(request.form['id'])
        booking_date = request.form['booking-date']
        booking_time = request.form['booking-time']

        # Create a new booking instance
        booking = Booking(id=booking_id, username=username, carname=carname, date=booking_date + ' ' + booking_time)

        # Add the booking to the session
        db.session.add(booking)
        db.session.commit()

    # Create a new booking instance
        booking = Booking(id=booking_id,username=username, carname=carname, date=booking_date + ' ' + booking_time)
    # ########3#################
        flash('You have successfully booked a car!', 'success')
        return redirect('/show_car')
    else:
        # If the username does not exist, redirect to the home.html page with an error message
        return render_template('chat.html')



@app.route('/show_car')
def showcar(): 
    return render_template('carinfo.html')  

@app.route('/view_car/<city>')
def view_car(city):
    try:
        return render_template(f'{city.lower()}_cars.html')
    except TemplateNotFound:
        abort(404)


@app.route('/carbookform', methods=['POST','GET'])
def carbookform(): 
    return render_template('carbook.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    # Connect to the database
    conn = db.engine.connect()

    # Output message if wrong
    msg = ''

    # Check if the user is already registered or not
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Creating variables
        username = request.form['username']
        password = request.form['password']

        # Query
        query = "SELECT * FROM signup WHERE username=%s AND password=%s"  # Updated query
        result = conn.execute(query, (username, password))
        account = result.fetchone()

        # If username and password are correct
        if account:
            # Set session
            session['loggedin'] = True
            session['username'] = account['username']
            session['password'] = account['password']

            return redirect(url_for('home'))
        # If username and password are wrong
        else:
            msg = "Invalid username or password"
    return render_template('login.html', msg=msg)



@app.route('/index')
def index():
    # Check if user is logged in or not
    if 'loggedin' in session:
        return render_template('paras.html', username=session['username'])
    return redirect(url_for('login'))


# my booking function
@app.route('/my_bookings')
def my_bookings():
    # Query the bookings from the database
    bookings = Booking.query.all()

    # Render the template with the bookings data
    return render_template('mybooking.html', bookings=bookings)
    




# cancel booking
from flask import request, redirect, flash

@app.route('/cancel_booking/<int:booking_id>', methods=['GET', 'POST'])
def cancel_booking(booking_id):
    # Query the booking from the database
    booking = Booking.query.get(booking_id)

    if booking:
        # Delete the booking from the session and commit the changes
        db.session.delete(booking)
        db.session.commit()

        # Display a flash message indicating successful cancellation
        flash('Booking canceled successfully!', 'success')
    else:
        # Display a flash message indicating booking not found
        flash('Booking not found.', 'error')

    # Redirect back to the "My Bookings" page
    return redirect('/show_car')




@app.route('/logout')
def logout():
    # Check if the user is logged in
    if 'loggedin' in session:
        # Forgetting session
        session.pop('loggedin', None)
        session.pop('username', None)
        session.pop('password', None)
        return redirect(url_for('login'))
    else:
        # If the user is not logged in, simply redirect to the login page
        return redirect(url_for('home'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Getting form values
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if username or email already exists in the database
        existing_user = Signup.query.filter(
            (Signup.username == username) | (Signup.email == email)
        ).first()

        if existing_user:
            # User with the same username or email already exists
            return "Username or email already exists. Please use another username or email."

        if existing_user:
            return render_template('signup.html')

        # Create a new Signup instance
        new_user = Signup(username=username, email=email, password=password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

    


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get the form values
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Create a new Contact instance
        entry = Contact(name=name, email=email, msg=message)

        # Adding the entry to the database
        db.session.add(entry)
        db.session.commit()

    return render_template('contact.html')


if __name__ == '__main__':
    app.run()


# @app.route('/')
# def home():
#     # return render_template('paras.html')
# #     @app.route('/')
# # def home():
#     csv_data = []
#     with open('car.csv', 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             csv_data.append(row)
#     return render_template('paras.html', csv_data=csv_data)
