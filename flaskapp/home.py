'''
    File: home.py
    Author: Drew Scott
    Description: Contains route for '/' 
'''

from main import *

@app.route("/", methods=['GET', 'POST'])
def home():
    conn = get_db_conn()
    cursor = conn.cursor()

    # get/create cookie (used to track trips data)
    cookie_id, cookie_token = get_cookie_info(cursor, request)
    conn.commit()
  
    user = None
    # get the username, and handle sign ups and logins
    try:
        user = handle_user(cursor, request, cookie_id)
        conn.commit()
    except AttributeError:
        return "Must fill all inputs"
    except RuntimeError as e:
        return str(e)

    response = make_response(render_template("index.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response
