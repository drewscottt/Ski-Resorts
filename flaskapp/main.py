'''
    File: main.py
    Author: Drew Scott
    Description: Contains route for '/' and methods required for all pages (i.e. cookies)
'''

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import MySQLdb
from datetime import datetime
import random, string

from passwords import DB, ALL_USER, ALL_PASSWORD, SELECT_USER, SELECT_PASSWORD

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    conn = get_db_conn()
    cursor = conn.cursor()

    # get/create cookie (used to track trips data), if user is specified, override the cookie sent in the request
    cookie_id, cookie_token, user = get_cookie_info(cursor, request)
    conn.commit()

    response = make_response(render_template("index.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response



'''
    BEGIN HELPER FUNCTIONS USED FOR ALL ROUTES
'''

def get_db_conn():
    '''
        Returns a connection to the database.
    '''

    conn = MySQLdb.connect(user=ALL_USER, password=ALL_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')

    return conn

def get_cookie_info(cursor, request):
    '''
        Returns the id of the trips_data cookie from the trips_data_cookies table, and the cookie token, and the username, if given.

        If the trips_data cookie isn't included in the request, this creates the cookie, then returns its id.

        If a username is specified in the request, return the cookie associated with that user (if the user
        doesn't already exist, create a new user)
    '''

    username = None
    if 'username' in request.args:
        username = request.args['username']

        query = "SELECT cookie_id FROM users WHERE username=%s"
        cursor.execute(query, (username, ))
        result = cursor.fetchall()
        if len(result) > 0:
            # user already exists
            cookie_id = result[0][0]

            # get the cookie
            query = "SELECT cookie FROM trips_data_cookies WHERE id=%s"
            cursor.execute(query, (cookie_id, ))
            cookie_token = cursor.fetchall()[0][0]

            return cookie_id, cookie_token, username

    # if here, either no username given, or the username given doesn't exist yet

    # get/create the cookie
    if 'trips_data' in request.cookies and 'logout' not in request.args:
        # get cookie from request if it exists and logout wasn't requested
        cookie_token = request.cookies['trips_data']
    else:
        # create cookie if it doesn't exist or logout was requested
        cookie_token = create_cookie(cursor)

    # get the cookie id
    query = "SELECT id FROM trips_data_cookies WHERE cookie=%s"
    cursor.execute(query, (cookie_token, ))
    cookie_id = cursor.fetchall()
    cookie_id = str(cookie_id[0][0])

    # handle username stuff
    if username is None:
        # if username not in the request, see if one already exists with this cookie
        query = "SELECT username FROM users WHERE cookie_id=%s"
        cursor.execute(query, (cookie_id, ))
        result = cursor.fetchall()
        if len(result) > 0:
            username = result[0][0]

    else:
        # if username in request, create new user and give it this cookie
        query = "INSERT INTO users (username, cookie_id) VALUES(%s, %s)"
        cursor.execute(query, (username, cookie_id))

    return cookie_id, cookie_token, username

def create_cookie(cursor):
    '''
        Returns a 16 length alpha-numeric string to represent the cookie value.
        It also adds this cookie to the trips_data_cookies table.
    '''

    token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    query = "INSERT INTO trips_data_cookies(cookie, time) VALUES(%s, %s)"
    now = datetime.now()

    cursor.execute(query, (token, now))

    cursor.execute("SELECT LAST_INSERT_ID()")
    cookie_id = cursor.fetchall()[0][0]

    query = f"CREATE TABLE trips_data_cookie{cookie_id}(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, resort_id INT, trip_id INT, FOREIGN KEY (resort_id) REFERENCES skiresorts(id), FOREIGN KEY (trip_id) REFERENCES trips(id))"

    cursor.execute(query)

    return token

