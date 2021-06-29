'''
    File: rest.py
    Author: Drew Scott
    Description: Contains REST API routes: /resorts, /resorts/<id>, /resorts/<name substring>, /state/<state name>
'''

from main import *

@app.route("/resorts", methods=["GET"])
def resorts():
    '''
        REST API route to show all resorts.
    '''

    conn = get_db_conn() 
    cursor = conn.cursor()

    query = "SELECT * FROM skiresorts"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    main_dict = skiresort_query_to_dict(result)
    
    return jsonify(main_dict)

@app.route("/<option>/<name>", methods=['GET'])
def rest(option, name):
    '''
        Specifies routes for REST API; valid options are: (state, resorts) and 
        name can be a state name if state is the option, or resorts substring or id if resorts is the option
    '''

    conn = get_db_conn() 
    cursor = conn.cursor()
    
    if option == 'state':
        query = "SELECT * FROM skiresorts WHERE state=%s;"
    elif option == 'resorts':
        if name.isdecimal():
            query = "SELECT * FROM skiresorts WHERE id=%s"
        else:
            name = '%%' + name + '%%'
            query = "SELECT * FROM skiresorts WHERE name LIKE %s"
    else:
        return make_response("Bad option", 404)

    cursor.execute(query, (name,))
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    main_dict = skiresort_query_to_dict(result)

    return jsonify(main_dict)

def skiresort_query_to_dict(result):
    '''
        Converts a result of a query of the form "SELECT * FROM skiresorts ..." to a dictionary
    '''

    main_dict = {}
    for res in result:
        sub_dict = {}
        sub_dict.update({"id": res[0]})
        sub_dict.update({"name": res[2]})
        sub_dict.update({"skiresort_info_page": res[1]})
        sub_dict.update({"state": res[4]})
        sub_dict.update({"website": res[3]})
        sub_dict.update({"latitude": res[5]})
        sub_dict.update({"longitude": res[6]})

        if "resorts" in main_dict:
            main_dict.update({"resorts": main_dict["resorts"] + [sub_dict]})
        else:
            main_dict.update({"resorts" : [sub_dict]})

    return main_dict
              
