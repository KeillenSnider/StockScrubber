# This is the brain of Flask and with stgart the web server, define routes, and handle the logic of the web app

#Flask for the app, render templates for getting html in templates, redirect for auto taking to next page, url for so nothing breaks
# request for getting if it is a post or get request, Sessions for keeping track if a user is logged in on every page
# make response turns the route output into a response object so we can add the no-cache header
from flask import Flask, render_template, redirect, url_for, request, session, make_response, jsonify
import database_stock_scrubber
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os
import fetcher

#_________________________________________________________________________________________________________

#Login required detector is needed
from functools import wraps
#Makes sure that the logged in user can not hit the back page button after logging out
#Wraps the route and makes sure it is not cached
def nocache(f):
    
    #Pretend to be f
    @wraps(f)

    #Lets it take any argument
    def decorated_function(*args, **kwargs):

        #Call the original function
        response = make_response(f(*args, **kwargs))

        #Says to not cache this page and get a new one
        response.headers['Cache-Control'] = 'no-store'


        return response
    
    return decorated_function


#This is to check if a user is logged into a session
def login_required(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):

        #Check if a user is logged in
        if 'username' not in session:

            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

#_________________________________________________________________________________________________________

load_dotenv()

#This starts the web app. __name__ is the current file, app is what routes will attach to and Flask is the framework
app = Flask(__name__)

#Gives 30 minutes of session time before it logs out the user for being inactive
app.permanent_session_lifetime = timedelta(minutes = 30)

#Key used to create sessions
app.secret_key = os.getenv('SECRET_KEY')

#Make sure the database is setup    
database_stock_scrubber.users_table()
database_stock_scrubber.watchlist_table()
database_stock_scrubber.alerts_table()

#_________________________________________________________________________________________________________

#Make the home page or where the url takes the user first
@app.route('/')
def home():
    #Go to the login page
    return redirect(url_for("login"))


#_________________________________________________________________________________________________________

#Login code
@app.route('/login', methods = ['GET', 'POST'])
@nocache
def login():

    #Check if it is a POST
    if request.method == 'POST':

        #get the user input
        username = request.form['username']
        password = request.form['password']


        #Check if the user exists and the password is right
        if database_stock_scrubber.verify_user(username, password):

            #Create a session because it returned True
            session.permanent = True
            
            #Give the session a username so it stays logged in on different pages
            session['username'] = username

            #Send them to the next page
            return redirect(url_for('dashboard'))
        
        #If no match send an error
        else:
            #Show the login page but send the error variable
            return render_template('login.html', error = "Invalid username or password")
    

    #If it is a GET then just show the page
    return render_template('login.html')

#_________________________________________________________________________________________________________

#Register code
@app.route('/register', methods = ['GET', 'POST'])
@nocache
def register():

    #Check if it was a POST
    if request.method == 'POST':

        #Get the username and password
        username = request.form['username']
        password = request.form['password']

        #Register the new user and see if the username is taken
        if database_stock_scrubber.create_user(username, password):

            #User is created and now they need toi login
            return redirect(url_for('login'))
        
        #Username is taken throw and error
        else:
            return render_template('register.html', error = "Username is already taken")
    

    #If a GET show the page
    return render_template('register.html')

#_________________________________________________________________________________________________________

#logout code
@app.route('/logout')
@nocache
def logout():
    #Clear the session data and return to the login page
    session.clear()
    return redirect(url_for('login'))

#_________________________________________________________________________________________________________

#Dashboard code
@app.route('/dashboard')
@nocache
@login_required
def dashboard():
    
    #Get the users id
    user = database_stock_scrubber.get_user(session['username'])
    user_id = user[0]
    
    #Get the users data
    watchlist = database_stock_scrubber.get_watchlist(user_id)
    alerts = database_stock_scrubber.get_alerts(user_id)

    #Send the data to dashboard so it has the username and all the table information
    return render_template('dashboard.html', username = session['username'], watchlist = watchlist, alerts = alerts)

#_________________________________________________________________________________________________________

#Add stock code
@app.route('/add_stock', methods = ['GET', 'POST'])
@nocache
@login_required
def add():

    #If it is a POST
    if request.method == 'POST':

        #Get the users id
        user = database_stock_scrubber.get_user(session['username'])
        user_id = user[0]

        #Get the data from the form
        symbol = request.form['symbol']
        threshold = float(request.form['threshold'])

        #Add the stock to the database
        database_stock_scrubber.add_stock(user_id, symbol, threshold)

        return redirect(url_for('dashboard'))
    
    #If a GET
    return render_template('add.html')

#_________________________________________________________________________________________________________

#Delete code
@app.route('/remove_stock/<int:stock_id>')
@nocache
@login_required
def delete(stock_id):

    #Delete the job
    database_stock_scrubber.delete_stock(stock_id)

    #Reload the dashboard
    return redirect(url_for('dashboard'))

#_________________________________________________________________________________________________________

#Prices code. Return stock prices
@app.route('/api/prices')
@nocache
@login_required
def prices():

    #use a Dictionary so yo can have key-value pairs
    prices = {} 

    #Get the users id
    user = database_stock_scrubber.get_user(session['username'])
    user_id = user[0]

    watchlist = database_stock_scrubber.get_watchlist(user_id)

    for stock in watchlist:
        symbol = stock[2]
        prices[symbol] = fetcher.price_check(symbol)
    
    return jsonify(prices)

#_________________________________________________________________________________________________________

if __name__ == "__main__":
    app.run(debug= os.getenv('DEBUG', 'False') == 'True')