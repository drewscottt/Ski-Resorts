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
  
    cookie_id, cookie_token, user = get_user_session_info(conn, cursor, request)
    conn.commit()

    email = None
    time_created = None
    if user is not None:
        query = "SELECT email FROM users WHERE cookie_id=%s"
        cursor.execute(query, (cookie_id, ))
        email = cursor.fetchall()[0][0] 

        query = "SELECT time FROM trips_data_cookies WHERE id=%s"
        cursor.execute(query, (cookie_id, ))
        time_created = cursor.fetchall()[0][0]

    cursor.close()
    conn.commit()
    conn.close()

    response = make_response(render_template("user.html", user=user, time_created=time_created, email=email))
    response.set_cookie("trips_data", cookie_token)

    return response
