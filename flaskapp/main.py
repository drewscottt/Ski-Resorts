'''
    File: main.py
    Author: Drew Scott
    Description: Contains routes for '/' and REST APIs, along with the appropriate helper functions for each.
'''

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import MySQLdb 
from datetime import datetime
import random, string

from passwords import DB, ALL_USER, ALL_PASSWORD, SELECT_USER, SELECT_PASSWORD

import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=['GET', 'POST'])
def home():
    conn = MySQLdb.connect(user=ALL_USER, password=ALL_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    # get/create cookie (used to track trips data), if user is specified, override the cookie sent in the request
    cookie_id, cookie_token, user = get_cookie_info(cursor, request)
    conn.commit()

    # get search and _type (used to get search information; search is the search term, and _type is the search type (resort or state))
    search, _type = get_search_params(request)

    if request.method == 'POST':
        # on POST, we have one of: (1) add resort, (2) update trip, (3) delete trip

        if 'delete_trip' in request.form:
            # delete trip
            resort_name = request.form['delete_trip']

            delete_resort_from_cookie(cursor, cookie_id, resort_name)

        elif 'update_trip' in request.form:
            # update trip
            resort_name = request.form['update_trip']
            start_date = request.form['start']
            end_date = request.form['end']

            people = []
            ages = []
            count = 1
            person_id = "person" + str(count)
            while person_id in request.form:
                people.append(request.form[person_id])
                ages.append(request.form['age' + str(count)])

                count += 1
                person_id = "person" + str(count)
    
            try:
                update_trip(cursor, cookie_id, resort_name, start_date, end_date, people, ages)
            except AttributeError:
                cursor.close()
                conn.close()
                return "Error: must set all parameters on update resort"

        elif 'add_trip' in request.form:
            # add trip
            resort_name = request.form['add_trip']

            add_resort_to_cookie(cursor, cookie_id, resort_name)    
        
        conn.commit()
    
    elif request.method == 'GET':
        # on GET, we need to get search results and trips info
        try:
            search_result = do_search(cursor, search, _type)

            # if no result returned, set to empty set to differentiate between invalid search and no search
            if search_result is None:
                search_result = ()

        except AttributeError:
            # invalid search
            search_result = None 

        trips = get_trips(cursor, cookie_id)

    cursor.close()
    conn.commit()
    conn.close()
    
    # send response, with all appropriate parameters and the cookie
    if request.method == 'POST':
        response = make_response(redirect(url_for('home', search=search, _type=_type, user=user)))
    elif request.method == 'GET':
        response = make_response(render_template("index.html", trips=trips, result=search_result, search=search, _type=_type, user=user)) 
    
    response.set_cookie('trips_data', cookie_token)
        
    return response

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

def get_search_params(request):
    '''
        Returns the search and _type parameters from the request.
        These can either be in the form (for POST) or args (for GET). 
    '''

    search = None
    if 'search' in request.args:
        search = request.args['search']
    elif 'search' in request.form:
        search = request.form['search']

    _type = None
    if '_type' in request.form:
        _type = request.form['_type']
    elif '_type' in request.args:
        _type = request.args['_type']

    return search, _type

def get_trips(cursor, cookie_id):
    '''
        Returns the trips data associated with this cookie.
       
        trips_data_cooke{cookie_id} has: resort_id and trip_id
        resort_id refers to skiresorts, trip_id refers to trips
       
        trips has: start, end, first_person
        first_person refers to people

        We return tuples of: (skiresorts.name, trips.start, trips.end, [(trips.first_person.name, trip.first_person.age), ...], (skiresorts.latitude, skiresorts.longitude))
    '''

    # this query should be safe, since we're generating the cookie_id
    query = f"SELECT * FROM trips_data_cookie{cookie_id}"
    cursor.execute(query)
    trips_data = cursor.fetchall()
    
    # get all of the trips data
    trips = []
    for trip in trips_data:
        resort_id = trip[1]
        trip_id = trip[2]

        # get resort_name, latitude, longitude
        query = "SELECT name, latitude, longitude FROM skiresorts WHERE id=%s"
        cursor.execute(query, (resort_id, ))
        resort_info = cursor.fetchall()
        resort_name = resort_info[0][0]
        resort_lat = resort_info[0][1]
        resort_long = resort_info[0][2]

        latlong = (resort_lat, resort_long)

        # get start, end, first_person
        query = "SELECT * FROM trips WHERE id=%s"
        cursor.execute(query, (trip_id,))
        trip_info = cursor.fetchall()

        if len(trip_info) > 0:
            start = trip_info[0][1]
            end = trip_info[0][2]
            person_id = trip_info[0][3]

            # get people
            people = []
            while person_id is not None:
                query = "SELECT * FROM people WHERE id=%s"
                cursor.execute(query, (person_id, ))
                person = cursor.fetchall()
                if len(person) > 0:
                    person_name = person[0][1]
                    person_age = person[0][2]
                    person_id = person[0][3]

                    person_tuple = (person_name, person_age)

                    people.append(person_tuple)
                else:
                    person_id = None

        else:
            start = None
            end = None
            people = None

        trip_tuple = (resort_name, start, end, people, latlong)
        trips.append(trip_tuple)

    return trips

def do_search(cursor, search, _type):
    '''
        Returns the search result for the search and _type params
    '''
    
    if search is None or _type is None:
        search_result = None
    else:
        wild_search = '%%' + search + '%%'

        if _type == 'name':
            query = "SELECT * FROM skiresorts WHERE name LIKE %s"
        elif _type == 'state':
            query = "SELECT * FROM skiresorts WHERE state LIKE %s"
        else:
            raise AttributeError

        cursor.execute(query, (wild_search, ))

        search_result = cursor.fetchall()

    return search_result

def update_trip(cursor, cookie_id, resort_name, start_date, end_date, people, ages):
    '''
        Updates the trip associated with the cookie and the resort_name (there is only one) with the new start, end, people, and ages.

        trips.start, trips.end, and trips.first_person is UPDATED (if the row for this trip already exists)
        
        new people are INSERTED into people with the corresponding ages, and the old people are DELETED from people
        people is formatted like a linked list (i.e. each row in people has a next id which refers to another row in people)
    '''

    # first, insert in new people
    people_ids = []
    count = 0
    # start with just name and age, save the ids for the next column
    for person in people:
        age = ages[count]
        query = "INSERT INTO people (name, age) VALUES (%s, %s)"
        cursor.execute(query, (person, age))
        cursor.execute("SELECT LAST_INSERT_ID()")
        person_id = cursor.fetchall()[0][0]
        people_ids.append(person_id)
        count += 1
    # then do next column
    prev_id = None
    for _id in people_ids:
        if prev_id is None:
            prev_id = _id
            continue

        query = "UPDATE people SET next=%s WHERE id=%s"
        cursor.execute(query, (_id, prev_id))
        
        prev_id = _id
    
    # get the resort id, so we can get the corresponding trip id
    query = "SELECT id FROM skiresorts WHERE name=%s"
    cursor.execute(query, (resort_name,))
    resort_id = cursor.fetchall()[0][0]

    query = f"SELECT trip_id FROM trips_data_cookie{cookie_id} WHERE resort_id=%s"
    cursor.execute(query, (resort_id, ))
    trips_id = cursor.fetchall()[0][0]
   
    # mySQL doesn't like empty strings as dates, so change to None/NULL
    if start_date == '':
        start_date = None
    if end_date == '':
        end_date = None

    # check start, end, and people are all defined, otherwise raise an error
    if start_date is None or end_date is None or len(people_ids) == 0:
        raise AttributeError
    
    # either create new row in trips table, or update the row
    if trips_id is None:
        # row doesn't already exist
        query = "INSERT INTO trips (start, end, first_person) VALUES (%s, %s, %s)"
        cursor.execute(query, (start_date, end_date, people_ids[0]))
    
        # get the id for this trip
        cursor.execute("SELECT LAST_INSERT_ID()")
        trips_id = cursor.fetchall()[0][0]
    
        # attach this trip id to this cookie's table where the resort is this one
        query = f"UPDATE trips_data_cookie{cookie_id} SET trip_id=%s WHERE resort_id=%s"
        cursor.execute(query, (trips_id, resort_id))
    
    else:
        # row already exists

        # first, delete old people
        query = "SELECT first_person FROM trips WHERE id=%s"
        cursor.execute(query, (trips_id,))
        first_person_id = cursor.fetchall()[0][0]
        
        delete_people(cursor, first_person_id)

        # update row
        query = "UPDATE trips SET start=%s, end=%s, first_person=%s WHERE id=%s"
        cursor.execute(query, (start_date, end_date, people_ids[0], trips_id))

def delete_people(cursor, first_person_id):
    '''
        Deletes all of the people from people which have next pointers from first_person_id
    '''

    old_id = first_person_id

    # people are formatted like linked list, so get next id before deleting current person (like free-ing)
    cursor.execute("SET foreign_key_checks = 0")
    while old_id is not None:
        query = "SELECT next FROM people WHERE id=%s"
        cursor.execute(query, (old_id, ))
        next_id = cursor.fetchall()[0][0]

        query = "DELETE FROM people WHERE id=%s"
        cursor.execute(query, (old_id,))
        
        old_id = next_id
    
    cursor.execute("SET foreign_key_checks = 1")


def delete_resort_from_cookie(cursor, cookie_id, resort_name):
    '''
        Deletes the trip associated with the cookie where the resort_id corresponds to the resort_name

        Includes: deleting from the cookie table, the trips table, and the people table
    '''

    # get id of resort
    query = "SELECT id FROM skiresorts WHERE name=%s"
    cursor.execute(query, (resort_name, ))
    resort_id = cursor.fetchall()[0][0]

    # get id of trip
    query = f"SELECT trip_id FROM trips_data_cookie{cookie_id} WHERE resort_id=%s"
    cursor.execute(query, (resort_id, ))
    trip_id = cursor.fetchall()[0][0]

    # get first_person id
    query = "SELECT first_person FROM trips WHERE id=%s"
    cursor.execute(query, (trip_id, ))
    result = cursor.fetchall()
    if len(result) > 0:
        first_person_id = cursor.fetchall()[0][0]
        
        # delete people associated with this trip
        delete_people(cursor, first_person_id)

    # delete the trips entry
    query = "DELETE FROM trips WHERE id=%s"
    cursor.execute(query, (trip_id, ))

    # delete trips_data_cookie entry for this resort
    query = f"DELETE FROM trips_data_cookie{cookie_id} WHERE resort_id=%s"
    cursor.execute(query, (resort_id, ))

def add_resort_to_cookie(cursor, cookie_id, resort):
    '''
        Inserts a new row into the table associated with this cookie_id, with this resort
    '''

    # check if a table associated with this cookie already exists
    query = "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = %s;"
    cursor.execute(query, ("trips_data_cookie" + str(cookie_id), ))
    result = cursor.fetchall()

    '''
        ALERT ALERT: BAD.
        I DIDN'T USE SAFE FORMAT STRING HERE. 
        FIX!!
    '''
    if not result:
        # make new table since the result was empty
        query = f"CREATE TABLE trips_data_cookie{cookie_id}(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, resort_id INT, trip_id INT, FOREIGN KEY (resort_id) REFERENCES skiresorts(id), FOREIGN KEY (trip_id) REFERENCES trips(id))"

        cursor.execute(query)

    # get the resort id of the resort
    query = "SELECT id FROM skiresorts WHERE name=%s"
    cursor.execute(query, (resort, ))
    resort_id = cursor.fetchall()
    resort_id = str(resort_id[0][0])

    # check if this resort already exists in the cookie table
    query = f"SELECT * FROM trips_data_cookie{cookie_id} WHERE resort_id=%s"
    cursor.execute(query, (resort_id, ))
    result = cursor.fetchall()

    if not result:
        # resort not already there, so add it
        query = f"INSERT INTO trips_data_cookie{cookie_id}(resort_id, trip_id) VALUES(%s, NULL)"

        cursor.execute(query, (resort_id, ))

'''
    END '/' ROUTES AND HELPERS;
    START REST API ROUTES AND HELPERS
'''

@app.route("/resorts", methods=["GET"])
def resorts():
    '''
        REST API route to show all resorts.
    '''

    conn = MySQLdb.connect(user=SELECT_USER, password=SELECT_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    query = "SELECT * FROM skiresorts"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    main_dict = skiresort_query_to_dict(result)
    
    return jsonify(main_dict)

@app.route("/<option>/<name>", methods=['GET'])
def rest(option, name):
    '''
        Specifies routes for REST API; valid options are: (state, resorts) and 
        name can be a state name if state is the option, or resorts substring or id if resorts is the option
    '''
    conn = MySQLdb.connect(user=SELECT_USER, password=SELECT_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()
    
    if option == 'state':
        query = "SELECT * FROM skiresorts WHERE state=%s;"
    elif option == 'resorts':
        if name.isdecimal():
            query = "SELECT * FROM skiresorts WHERE id=%s"
        else:
            name = '%%' + name + '%%'
            query = "SELECT * FROM skiresorts WHERE name LIKE %s"
    else:
        return make_response("Bad option", 404)

    cursor.execute(query, (name,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    
    main_dict = skiresort_query_to_dict(result)

    return jsonify(main_dict)

def skiresort_query_to_dict(result):
    '''
        Converts a result of a query of the form "SELECT * FROM skiresorts ..." to a dictionary
    '''

    main_dict = {}
    for res in result:
        sub_dict = {}
        sub_dict.update({"id": res[0]})
        sub_dict.update({"name": res[2]})
        sub_dict.update({"skiresort_info_page": res[1]})
        sub_dict.update({"state": res[4]})
        sub_dict.update({"website": res[3]})
        sub_dict.update({"latitude": res[5]})
        sub_dict.update({"longitude": res[6]})

        if "resorts" in main_dict:
            main_dict.update({"resorts": main_dict["resorts"] + [sub_dict]})
        else:
            main_dict.update({"resorts" : [sub_dict]})

    return main_dict
