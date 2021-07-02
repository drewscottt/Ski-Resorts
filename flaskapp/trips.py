'''
    File: trips.py
    Author: Drew Scott
    Description: Contains route for '/trips' 
'''

from main import *

@app.route("/trips", methods=['GET', 'POST'])
def trips():
    conn = get_db_conn()
    cursor = conn.cursor()

    cookie_id, cookie_token, user = get_user_session_info(conn, cursor, request)
    conn.commit()
  
    cursor.close()
    conn.commit()
    conn.close()
    
    response = make_response(render_template("trips.html", user=user))
    response.set_cookie("trips_data", cookie_token)

    return response
