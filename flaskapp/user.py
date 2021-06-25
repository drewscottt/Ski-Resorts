'''
    File: user.py
    Author: Drew Scott
    Description: Contains route for '/user'
'''

from main import *

@app.route("/user", methods=['GET'])
def user():
    conn = MySQLdb.connect(user=ALL_USER, password=ALL_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    # get/create cookie (used to track trips data), if user is specified, override the cookie sent in the request
    cookie_id, cookie_token, user = get_cookie_info(cursor, request)
    conn.commit()

    response = make_response(render_template("user.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response
