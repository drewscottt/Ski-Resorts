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
    
    # get/create cookie (used to track trips data)
    cookie_id, cookie_token = get_cookie_info(cursor, request)
    conn.commit()
    
    # get the username, and handle sign ups and logins
    try:
        user = handle_user(cursor, request, cookie_id)
        conn.commit()
    except AttributeError:
        return "Must fill all inputs"
    except RuntimeError as e:
        return str(e)

    response = make_response(render_template("trips.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response

