'''
    File: user.py
    Author: Drew Scott
    Description: Contains route for '/user'
'''

from main import *

@app.route("/user", methods=['GET'])
def user():
    conn = get_db_conn() 
    cursor = conn.cursor()

    # get/create cookie (used to track trips data), if user is specified, override the cookie sent in the request
    cookie_id, cookie_token, user = get_cookie_info(cursor, request)
    conn.commit()

    time_created = None
    if user is not None:
        query = "SELECT time FROM trips_data_cookies WHERE id=%s"
        cursor.execute(query, (cookie_id, ))

        time_created = cursor.fetchall()[0][0]

    response = make_response(render_template("user.html", user=user, time_created=time_created))
    response.set_cookie("trips_data", cookie_token)

    return response
