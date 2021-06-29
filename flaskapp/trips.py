'''
    File: trips.py
    Author: Drew Scott
    Description: Contains route for '/trips' 
'''

from main import *

@app.route("/trips", methods=['GET'])
def trips():
    conn = get_db_conn() 
    cursor = conn.cursor()

    # get/create cookie (used to track trips data), if user is specified, override the cookie sent in the request
    cookie_id, cookie_token, user = get_cookie_info(cursor, request)
    conn.commit()

    response = make_response(render_template("trips.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response

