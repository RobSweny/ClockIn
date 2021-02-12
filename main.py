from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_restful import Api, Resource, reqparse
from datetime import datetime
import json
from operator import itemgetter 

users = []

# Create instance of a Flask application
app = Flask(__name__)
api = Api(app)
app.secret_key = 'topsecretkeywritteninplaintext'

class User:
    def __init__(self, id, username, password, admin):
        self.id = id
        self.username = username
        self.password = password
        self.admin = admin

    # Official string conversion of an object
    def __repr__(self):
        return f'<User: {self.username}';

users.append(User(id=1, username='Ana', password='password', admin='false'))
users.append(User(id=2, username='Rob', password='password', admin='true'))



today = datetime.today().strftime('%Y%m%d')
now = datetime.now().strftime('%H:%M:%S')
punchcards = {"00001": {"date": str(today), "clock-in": str("08:30:00"), "clock-out": str("17:00:01"), "holiday": False},
        "00002": {"date": str(today), "clock-in": str("08:30:00"), "clock-out": str("12:30:00"), "holiday": True},
        "00003": {"date": str(today), "clock-in": str("08:30:00"), "clock-out": str("12:30:00"), "holiday": False}}

# Required fields
# punchcard_get_args = reqparse.RequestParser()
# punchcard_get_args.add_argument("punchcard", type=str, help="Employee ID is required", required=True)

# convert time to to seconds, this is used for comparisons between times
def TimeToSecondsConvert(t):
    h, m, s = [int(i) for i in t.split(':')]
    return 3600*h + 60*m + s


@app.route('/login', methods=['POST', 'GET'])
def login():
    # Check request type
    if request.method == 'POST':
        session.pop('_flashes', None)
        # If user_id is already in the session, 
        try: 
            session.pop('user_id', None)
        except Exception as e:
            print('No user to pop!')

        username = request.form['username']
        password = request.form['password']

        # Check if the username inputted is in the list of users
        try:
            user = [x for x in users if x.username == username][0]
        except Exception:
            flash('Invalid Credentials')
            return redirect(url_for('login'))
        if user and user.password == password:
            #session['user_id'] == user.id
            # url_for = URL builder 
            flash('You have successfully logged in')
            return redirect(url_for('profile'))
    
        flash('Invalid Credentials')
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

# Retrieve all punchcards
class PunchCardsAll(Resource):
    def get(self):
        return punchcards


# Retrieve data from employee based on ID number
class PunchCardsID(Resource):
    def get(self, punchcard):
        return punchcards[punchcard]


# Retrieve data from employee based on ID number
class PunchCardsID(Resource):
    def get(self, punchcard):
        return punchcards[punchcard]


# Retrieve all clock in times
class PunchCardsClockIn(Resource):
    def get(self):
        res = []
        for each in punchcards.items():
            res.append(each[1]['clock-in'])
        return res


# Retrieve all clock out times
class PunchCardsClockOut(Resource):
    def get(self):
        res = []
        for each in punchcards.items():
            res.append(each[1]['clock-out'])
        return res


# Retrieve Hours work per worker
class HoursWorked(Resource):
    def get(self):
        res = []
        for each in punchcards.items():
            date_time_clock_out = datetime.strptime(each[1]['clock-out'], '%H:%M:%S')
            date_time_clock_in = datetime.strptime(each[1]['clock-in'], '%H:%M:%S')
            hours_worked = date_time_clock_out - date_time_clock_in
            res.append("User ID: " + each[0] + ", hours worked: " +  str(hours_worked))
        return res


# Retrieve list of users who worked less hours then they should
class HoursBelowTime(Resource):
    def get(self):
        res = []
        defined_hours = "08:00:00"
        for each in punchcards.items():
            date_time_clock_out = datetime.strptime(each[1]['clock-out'], '%H:%M:%S')
            date_time_clock_in = datetime.strptime(each[1]['clock-in'], '%H:%M:%S')
            holiday = each[1]['holiday']
            hours_worked = date_time_clock_out - date_time_clock_in
            hours_worked_seconds = TimeToSecondsConvert(str(hours_worked))
            defined_hours_seconds = TimeToSecondsConvert(str(defined_hours))
            if(hours_worked_seconds < defined_hours_seconds and not holiday):
                res.append("User ID: " + each[0] + ", Hours worked: " +  str(hours_worked) + ", Holiday: " + str(each[1]['holiday']))
        return res
 


# Function to check how many employess clocked in today
# Enter /PunchCardsDate/<string:date>" with date as parameter format (%Y%m%d)
class PunchCardsDate(Resource):
    def get(self, date):
        counter = 0
        for each in punchcards.items():
            if (each[1]['date'] == date):
                counter += 1
        return counter


# The add_resource function registers the routes with the framework using the given endpoint.
# If an endpoint isn't given then Flask-RESTful generates one for you from the class name
# <> parameter
api.add_resource(PunchCardsID, "/PunchCardsID/<string:punchcard>")
api.add_resource(PunchCardsAll, "/PunchCardsAll")
api.add_resource(PunchCardsClockIn, "/PunchCardsClockIn")
api.add_resource(PunchCardsClockOut, "/PunchCardsClockOut")
api.add_resource(PunchCardsDate, "/PunchCardsDate/<string:date>")
api.add_resource(HoursWorked, "/HoursWorked")
api.add_resource(HoursBelowTime, "/HoursBelowTime")



# Run the app
if __name__ == "__main__":
    app.run(debug=True)





