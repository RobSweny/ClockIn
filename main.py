from flask import Flask, redirect, url_for, render_template, request, session, flash, g
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_principal import Principal
from werkzeug.security import generate_password_hash, check_password_hash
from firebase import firebase
from datetime import datetime
import json
from operator import itemgetter 

users = []

# Create instance of a Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'topsecretkeywritteninplaintext'
app.secret_key = 'topsecretkeywritteninplaintext'
principals = Principal(app)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "example.com"}})

firebase = firebase.FirebaseApplication('https://clockin-440c9-default-rtdb.europe-west1.firebasedatabase.app/', None)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user


class User:
    def __init__(self, id, username, password, admin):
        self.id = id
        self.username = username
        self.password = password
        self.admin = admin

    # Official string conversion of an object
    def __repr__(self):
        return f'User: {self.username}'

users.append(User(id=1, username='Ana', password="password", admin=False))
users.append(User(id=2, username='Rob', password="password", admin=True))



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
            session["user_id"] = user.id
            session["user_admin"] = user.admin
            # url_for = URL builder 
            flash('You have successfully logged in')
            session.pop('_flashes', None)
            return redirect(url_for('profile'))

                
        flash('Invalid Credentials')
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/')
def hometest():
    result = firebase.get('/users', None)
    return str(result)


@app.route('/submit/add/', endpoint='add', methods=["POST", "GET"])
@app.route('/submit/remove/', endpoint='remove', methods=["POST", "GET"])
def submitAdd():
    if request.method == 'POST':
        if request.endpoint == 'add':
            session.pop('_flashes', None)
            userdata = dict(request.form)
            name = userdata["fullname"]
            password = userdata["password"]
            admin = userdata['dropdown']
            admin = False if 1 else True
            print(admin)
            new_data = {"fullname": name, "password": password, "clock-in": None, "clock-out": None, "date": datetime.today().strftime("%Y%m%d"), "holiday": None, "admin": admin}
            firebase.post("/users", new_data)
            flash('Successfully added user to the database!')
            return redirect(url_for('profile'))
        else: 
            session.pop('_flashes', None)
            userdata = dict(request.form)
            name = userdata["fullname"]
            result = firebase.get('/users', None)
            for key, value in result.items():
                if value["fullname"] == name:
                    try:
                       firebase.delete("/users", key)
                    except Exception as e:
                        print("Issue removing user " + str(e))        
            flash('Successfully removed user from database!')
            return redirect(url_for('profile'))
    else:
        return "Sorry, there was an error."


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not g.user:
        flash('Please login to view your profile!')
        return redirect(url_for('login'))

    result = firebase.get('/users', None)
    triggered = False
    # Retrieve all users
    if not g.user.admin:
        for key, value in result.items():
            if value["fullname"] == g.user.username:
                try:
                    result = dict({'key': key, 'value': value})
                    triggered = True
                except Exception as e:
                    print(str(e))
    if not triggered:
        result = {}
    return render_template("profile.html", result=result)
    


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
        if g.user.admin:
            res = []
            for each in punchcards.items():
                res.append(each[1]['clock-in'])
            return res
        else:
            flash('You need to be an administrator to view this')
            return redirect(url_for('login'))
        


# Retrieve all clock out times
class PunchCardsClockOut(Resource):
    def get(self):
        if g.user.admin:
            res = []
            for each in punchcards.items():
                res.append(each[1]['clock-out'])
            return res
        else:
            flash('You need to be an administrator to view this')
            return redirect(url_for('login'))


# Retrieve Hours work per worker
class HoursWorked(Resource):
    def get(self):
        if g.user.admin:
            res = []
            for each in punchcards.items():
                date_time_clock_out = datetime.strptime(each[1]['clock-out'], '%H:%M:%S')
                date_time_clock_in = datetime.strptime(each[1]['clock-in'], '%H:%M:%S')
                hours_worked = date_time_clock_out - date_time_clock_in
                res.append("User ID: " + each[0] + ", hours worked: " +  str(hours_worked))
            return res
        else:
            flash('You need to be an administrator to view this')
            return redirect(url_for('login'))


# Retrieve list of users who worked less hours then they should
class HoursBelowTime(Resource):
    def get(self):
        if g.user.admin:
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
        else:
            flash('You need to be an administrator to view this')
            return redirect(url_for('login'))
 


# Function to check how many employess clocked in today
# Enter /PunchCardsDate/<string:date>" with date as parameter format (%Y%m%d)
class PunchCardsDate(Resource):
    def get(self, date):
        if g.user.admin:
            counter = 0
            for each in punchcards.items():
                if (each[1]['date'] == date):
                    counter += 1
            return counter
        else:
            flash('You need to be an administrator to view this')
            return redirect(url_for('login'))


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





