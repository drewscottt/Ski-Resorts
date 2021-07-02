'''
    File: main.py
    Author: Drew Scott
    Description: Contains imports and helper functions used on all pages.
                 Use 'from main import *' in all other pages
'''

import sys

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import MySQLdb
from datetime import datetime
import random, string
from passlib.hash import sha256_crypt

from passwords import DB, ALL_USER, ALL_PASSWORD, SELECT_USER, SELECT_PASSWORD

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

def get_db_conn():
    '''
        Returns a connection to the database.
    '''

    return MySQLdb.connect(user=ALL_USER, password=ALL_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')

'''
    START user stuff
'''

def get_user_session_info(conn, cursor, request):
    # get cookie info from request.cookies
    # if a cookie wasn't sent, we will create one
    cookie_id, cookie_token = get_cookie_info(cursor, request)
    conn.commit()

    # get cookie/user info from login request
    # if a login was successful, we will change the cookie_id and cookie_token to the ones associated with the user
    user, new_cookie_id, new_cookie_token = handle_user(cursor, request, cookie_id)
    if new_cookie_id is not None and new_cookie_token is not None:
        # swap cookie_id and cookie_token
        cookie_id = new_cookie_id
        cookie_token = new_cookie_token

    return cookie_id, cookie_token, user

def handle_user(cursor, request, cookie_id):
    '''
        Returns the username of the user in the request. Handles create account and login requests
    '''
    
    user = None
    new_cookie_id = None
    new_cookie_token = None

    # check if a sign up or login was requested
    if 'username' in request.form and 'password' in request.form:
        if 'email' in request.form:
            # sign up requested
            user = create_user(cursor, request, cookie_id)
        else:
            # login requested
            user = login_user(cursor, request)
            if user is not None:
                query = "SELECT cookie_id FROM users WHERE username=%s"
                cursor.execute(query, (user, ))
                new_cookie_id = cursor.fetchall()[0][0]
            
                query = "SELECT cookie FROM trips_data_cookies WHERE id=%s"
                cursor.execute(query, (new_cookie_id, ))
                new_cookie_token = cursor.fetchall()[0][0]

    elif 'trips_data' in request.cookies:
        query = "SELECT username FROM users WHERE cookie_id=%s"
        cursor.execute(query, (cookie_id, ))
        result = cursor.fetchall()
        if len(result) > 0:
            user = result[0][0]

    return user, new_cookie_id, new_cookie_token

def login_user(cursor, request):
    '''
        Returns the username associated with the request if the login is valid, returns None if username exists, but login was invalid
        
        Errors raised when: username or password aren't defined in request.form
        And when there isn't a user in the users table that has the username/email specified in request.form
    '''

    # extract values from request
    user = request.form['username']
    password = request.form['password']
    
    # make sure username and password are defined
    if len(user) == 0 or len(password) == 0: 
        raise AttributeError("All fields must be defined")

    # user can be either a username or an email

    # check the username
    query = "SELECT password FROM users WHERE username=%s"
    cursor.execute(query, (user, ))
    stored_hash = cursor.fetchall()
    if len(stored_hash) > 0:
        if check_pass(password, stored_hash[0][0]):
            return user
        return None
        
    # check the password
    query = "SELECT password FROM users WHERE email=%s"
    cursor.execute(query, (user, ))
    stored_hash = cursor.fetchall()
    if len(stored_hash) > 0:
        if check_pass(password, stored_hash[0][0]):
            query = "SELECT username FROM users WHERE email=%s"
            cursor.execute(query, (user, ))
            return cursor.fetchall()[0][0]
        return None

    # a user with the username/email specified doesn't exist
    raise RuntimeError("User with the input username/email doesn't exist")

def create_user(cursor, request, cookie_id):
    '''
        Adds a new user to the users table using the request.form

        Errors raised when: not all of email, username, password are defined in request
        And when a user with the specified username or email already exists
    '''

    # extract values from request
    email = request.form['email']
    username = request.form['username']
    password = request.form['password']
    
    # make sure all values are defined in the request.form (email, username, password)
    if len(email) == 0 or len(username) == 0 or len(password) == 0: 
        raise AttributeError("All fields must be filled")

    # check that a user with this name doesn't already exist
    query = "SELECT * FROM users WHERE username=%s"
    cursor.execute(query, (username, ))
    if len(cursor.fetchall()) > 0:
        raise RuntimeError("User with this username already exists")

    # check that a user with this email doesn't already exist
    query = "SELECT * FROM users WHERE email=%s"
    cursor.execute(query, (email, ))
    if len(cursor.fetchall()) > 0:
        raise RuntimeError("User with this email already exists")

    pass_hash = get_hash(password)

    query = "INSERT INTO users (email, username, password, cookie_id) VALUES(%s, %s, %s, %s)"
    cursor.execute(query, (email, username, pass_hash, cookie_id))

    return username

def check_pass(input_pass, stored_hash):
    '''
        Returns True if input_pass and stored_hash correspond 
        Returns False otherwise
    '''
    
    return sha256_crypt.verify(input_pass, stored_hash)

def get_hash(raw_pass):
    '''
        Returns hash of raw_pass (77 length)
    '''

    return sha256_crypt.encrypt(raw_pass)

'''
    START cookie stuff
'''

def get_cookie_info(cursor, request):
    '''
        Returns id and token associated with the trips_data cookie from the request

        If the trips_data cookie isn't included in the request, this creates the cookie, then returns its id.
    '''

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

    # check that this cookie exists in the table (it could've gotten deleted or just be invalid)
    # if it doesn't, make a new cookie
    if len(cookie_id) == 0:
        cookie_token = create_cookie(cursor)
        cursor.execute(query, (cookie_token, ))
        cookie_id = cursor.fetchall()

    cookie_id = str(cookie_id[0][0])

    return cookie_id, cookie_token

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
 
