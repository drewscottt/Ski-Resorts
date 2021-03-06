'''
    File: clear_unused_cookies.py
    Author: Drew Scott
    Description: Checks all cookies created more than 1 hour ago. Deletes them if there are no trips data and no user associated with them.
'''

import MySQLdb
from passwords import DB, USER, PASSWORD 
from datetime import datetime, timedelta
import time

def main():
    conn = MySQLdb.connect(user=USER, password=PASSWORD, host='localhost', database=DB, auth_plugin='mysql_native_password')
    cursor = conn.cursor()

    # cookie can be unused if it was created more than an hour ago
    now = datetime.now()
    cookie_length = timedelta(hours=1)
    threshold = now - cookie_length 

    query = "SELECT * FROM trips_data_cookies WHERE time<%s"
    cursor.execute(query, (threshold, ))

    candidates = cursor.fetchall()

    # check candidates for trips and user data (if they have a separate trips_data_cookie<id> table or if that table is empty)
    for c in candidates:
        c_id = c[0]

        # check if cookie has user associated with it
        if has_user(cursor, c_id):
            # this cookie has a user, so don't delete it
            continue

        # check if c has a trips_data_cookie<c_id> table
        table_name = f"trips_data_cookie{c_id}"
        query = "SHOW TABLES LIKE %s"
        cursor.execute(query, (table_name, ))
        table_exists = len(cursor.fetchall()) == 1

        if not table_exists:
            # c doesn't have trips or user associated with it, so delete it
            query = "DELETE FROM trips_data_cookies WHERE id=%s"
            cursor.execute(query, (c_id, ))
        else:
            # c has a table, so check if it's empty
            query = f"SELECT * FROM {table_name}"
            cursor.execute(query)
            table_empty = len(cursor.fetchall()) == 0
            
            if table_empty:
                # table is empty, so drop it and delete the row
                query = f"DROP TABLE {table_name}"
                cursor.execute(query)

                query = f"DELETE FROM trips_data_cookies WHERE id=%s"
                cursor.execute(query, (c_id, ))

    # check if there are any trips_data_cookie<id> tables that don't have a row associated with them in trips_data_cookies
    query = "SHOW TABLES LIKE 'trips_data_cookie%'"
    cursor.execute(query)
    candidates = cursor.fetchall()

    for c in candidates:
        # get the id for this table
        prefix = "trips_data_cookie"
        table_name = c[0]
        c_id = table_name[ len(prefix) : ]

        if not c_id.isnumeric():
            continue

        # check if row exists with this id
        query = "SELECT * FROM trips_data_cookies WHERE id=%s"
        cursor.execute(query, (c_id, ))
        row_exists = len(cursor.fetchall()) == 1
        if not row_exists:
            # row doesn't exist, so drop the table
            query = f"DROP TABLE {table_name}"
            cursor.execute(query)

    cursor.close()
    conn.commit()
    conn.close()

def has_user(cursor, cookie_id):
    query = "SELECT * FROM users WHERE cookie_id=%s"
    cursor.execute(query, (cookie_id, ))
    return len(cursor.fetchall()) != 0

if __name__ == "__main__":
    while True:
        main()
        # sleep for an hour
        time.sleep(3600)
