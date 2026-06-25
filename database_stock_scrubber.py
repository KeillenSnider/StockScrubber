#Will be the database file for Stock Scrubber

import psycopg2
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()



#Get the url used to talk to the database
def get_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

#____________________________________________________________________________________________________________________________________

#Users Tabel
def users_table():

    connection = get_connection()

    cursor = connection.cursor()


    #Create the database and set up the columns
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL        
        )               

    """)

    connection.commit()

    connection.close()



#Create a user and put them in the table
def create_user(username,password):

    connection = get_connection()

    cursor = connection.cursor()

    #PostgreSQL stores text not bytes so you have to convert to a string at the end from bytes
    #Hash the password with bcrypt and salt so no password is hashed the same
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    #Try to insert the user and see if the username is not taken
    try:

        cursor.execute("""
            INSERT INTO users (username, password_hash) VALUES (%s, %s)
        """, (username, password_hash))

        connection.commit()

        connection.close()
        
        return True
    except:
        connection.close()

        return False
    

#Make sure the user has an account and also the right password
def verify_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    #Get all the usernames to see if one matches if it does get the information
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    connection.close()

    #If no user then ask them to register
    if not user:
        return False
    

    #Check password and since PostgreSQL stores as text you need to turn it back into bytes
    stored_hash = user[2].encode('utf-8')

    #Checks the passwords with eachother and sees if they match if not it returns false
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)



#Gets all the users data and returns it so I can use it later if I need it
def get_user(username):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

    user = cursor.fetchone()

    connection.close()

    return user



#____________________________________________________________________________________________________________________________________

#Table for the users watchlist of stocks
def watchlist_table():

    connection = get_connection()

    cursor = connection.cursor()

    #Incase it has not been called yet
    users_table()


    #Create the table with a key referencing the users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist(
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            symbol TEXT NOT NULL,
            name TEXT DEFAULT NULL,
            threshold FLOAT NOT NULL
        )
    """)

    connection.commit()

    connection.close()



#Add a stock to the watchlsit
def add_stock(user_id, symbol, name, threshold):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO watchlist(user_id, symbol, name, threshold) VALUES(%s, %s, %s, %s)
    """, (user_id, symbol, name, threshold))

    connection.commit()

    connection.close()


#Delete a stock
def delete_stock(stock_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("DELETE FROM watchlist WHERE id = %s", (stock_id,))

    connection.commit()

    connection.close()


#Get everything in a users watchlist
def get_watchlist(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM watchlist WHERE user_id = %s ORDER BY symbol ASC", (user_id,))

    #Gets the table of information that the user has
    table = cursor.fetchall()

    connection.close()

    return table




#____________________________________________________________________________________________________________________________________

#Table for the alerts so that they are saved and can be looked back on
def alerts_table():

    connection = get_connection()

    cursor = connection.cursor()

    #Incase it has not been called yet
    users_table()

    # Create a table that references the user for alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts(
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            symbol TEXT NOT NULL,
            old_price FLOAT NOT NULL,
            new_price FLOAT NOT NULL,
            difference FLOAT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()



#Saves an alert to the table
def save_alert(user_id, symbol, old_price, new_price, difference, message):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO alerts(user_id, symbol, old_price, new_price, difference, message) VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, symbol, old_price, new_price, difference, message))

    connection.commit()

    connection.close()


#Get all the alerts
def get_alerts(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM alerts WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))

    table = cursor.fetchall()

    connection.close()

    return table


#Used so only when this file is ran it will work not if it is called in another file
if __name__ == "__main__":
    users_table()
    watchlist_table()
    alerts_table()