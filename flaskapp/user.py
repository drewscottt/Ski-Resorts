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

    cursor.close()
    conn.commit()
    conn.close()

    time_created = None
    if user is not None:
        query = "SELECT time FROM trips_data_cookies WHERE id=%s"
        cursor.execute(query, (cookie_id, ))

        time_created = cursor.fetchall()[0][0]

    cursor.close()
    conn.commit()
    conn.close()

    response = make_response(render_template("user.html", user=user, time_created=time_created))
    response.set_cookie("trips_data", cookie_token)

    return response
