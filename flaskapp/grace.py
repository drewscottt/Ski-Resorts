from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import MySQLdb
from datetime import datetime

from passwords import DB, GRACE_USER, GRACE_PASSWORD

from main import app

@app.route("/grace", methods=['GET', 'POST'])
def grace():
    conn = MySQLdb.connect(user=GRACE_USER, password=GRACE_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    cookie_token = get_cookie_info(cursor, request)

    if request.method == 'POST':
        if len(request.form) == 2:
            query = 'INSERT INTO grace_comments (message, user, time) VALUES(%s, %s, %s)'

            now = datetime.now()
            message = request.form['message']
            user = request.form['user']

            cursor.execute(query, (message, user, now))
        else:
            query = 'DELETE FROM grace_comments WHERE id=%s'

            comment_id = request.form['id']
            cursor.execute(query, (comment_id,))

    query = 'SELECT * FROM grace_comments'
    cursor.execute(query)
    comments = cursor.fetchall()

    cursor.close()
    conn.commit()
    conn.close()

    if request.method == 'POST':
        response = make_response(redirect(url_for("grace")))
    else:
        response = make_response(render_template("grace.html", comments=comments))

    response.set_cookie('grace_cookie', cookie_token)

    return response

def get_cookie_info(cursor, request):
    if 'grace_cookie' in request.cookies:
        cookie_token = request.cookies['grace_cookie']
    else:
        cookie_token = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        

    return cookie_token



