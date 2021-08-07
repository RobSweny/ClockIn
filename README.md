<h1>Flask Clock in System</h1>

Flask server for managing a clock in / clock out system

This allows an administrator to check information on the user data based on their working hours<br>
Administrators are the only users available to view data and add new users to the system<br>
Users clock in and data is sent to firebase 

#### - User punch card data
```python
punchcards = {"00001": {"date": str(today), "clock-in": str("08:30:00"), "clock-out": str("17:00:01"), "holiday": False},
```

<h2> Primary functions under: </h2> 
https://github.com/RobSweny/ClockIn/blob/main/main.py


#### - Function to check how many employess clocked in today<br/>Enter /PunchCardsDate/<string:date>" with date as parameter format (%Y%m%d)
```python
class PunchCardsDate(Resource)
```

#### - Retrieve list of users who worked less hours then they should
```python
class HoursBelowTime(Resource)
```

#### - Retrieve Hours work per worker
```python
class HoursWorked(Resource)
```

#### - Retrieve all clock out times
```python
class PunchCardsClockOut(Resource)
```

#### - Retrieve all clock in times
```python
class PunchCardsClockIn(Resource)
```

#### -  Retrieve data from employee based on ID number
```python
class PunchCardsID(Resource)
```

#### -  Retrieve data from employee based on ID number
```python
class PunchCardsID(Resource)
```
