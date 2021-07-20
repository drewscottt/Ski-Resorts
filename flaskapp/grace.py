'''
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
import MySQLdb
from datetime import datetime

from passwords import DB, GRACE_USER, GRACE_PASSWORD

from main import app

@app.route("/grace", methods=['GET', 'POST'])
def grace():
    conn = MySQLdb.connect(user=GRACE_USER, password=GRACE_PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')

    if request.method == 'POST':
        if len(request.form) == 2:
            cursor = conn.cursor()
            query = 'INSERT INTO grace_comments (message, user, time) VALUES(%s, %s, %s)'

            now = datetime.now()
            message = request.form['message']
            user = request.form['user']

            cursor.execute(query, (message, user, now))
            cursor.close()
            conn.commit()
        else:
            cursor = conn.cursor()
            query = 'DELETE FROM grace_comments WHERE id=%s'

            comment_id = request.form['id']
            cursor.execute(query, (comment_id,))

            cursor.close()
            conn.commit()

    cursor = conn.cursor()
    query = 'SELECT * FROM grace_comments'
    cursor.execute(query)
    comments = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        return redirect(url_for("grace"))

    return render_template("grace.html", comments=comments)
'''
