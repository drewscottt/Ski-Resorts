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

    try:
        cookie_id, cookie_token, user = get_user_session_info(conn, cursor, request)
        conn.commit()
    except Exception as e:
        return str(e)

    cursor.close()
    conn.commit()
    conn.close()
   
    if request.method == 'POST':
        response = make_response(redirect(url_for('home', user=user)))
    else:
        response = make_response(render_template("index.html", user=user))
    
    response.set_cookie("trips_data", cookie_token)

    return response
