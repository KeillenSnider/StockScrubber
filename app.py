# This is the brain of Flask and with stgart the web server, define routes, and handle the logic of the web app

#Flask for the app, render templates for getting html in templates, redirect for auto taking to next page, url for so nothing breaks
# request for getting if it is a post or get request, Sessions for keeping track if a user is logged in on every page
# make response turns the route output into a response object so we can add the no-cache header
from flask import Flask, render_template, redirect, url_for, request, session, make_response
import database_stock_scrubber
from datetime import timedelta, datetime
from dotenv import load_dotenv
import os

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


load_dotenv()

#This starts the web app. __name__ is the current file, app is what routes will attach to and Flask is the framework
app = Flask(__name__)

#Gives 30 minutes of session time before it logs out the user for being inactive
app.permanent_session_lifetime = timedelta(minutes = 30)

#Key used to create sessions
app.secret_key = os.getenv('SECRET_KEY')