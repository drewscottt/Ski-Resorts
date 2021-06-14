'''
    File: skiresorts_xlsx.py
    Author: Drew Scott
    Description: Makes '../skiresorts/skiresorts.xlsx' with columns: 'skiresorts.info link', Name, Website, and State.
                 Requires html files for skiresorts.info main and tourist pages. And a list of all of the links to the main
                 skiresorts.info pages.
'''

from xlsxwriter import Workbook
from bs4 import BeautifulSoup
import requests
import json

def get_name(resort_file):
    soup = BeautifulSoup(resort_file, 'html.parser')
    
    # the name is in the first h1 tag
    h1 = str(soup.find_all('h1')[0])

    # these are all the possible prefixes for the name
    res_txt = "Ski resort "
    in_txt = "Indoor ski area "
    dry_txt = "Dry slopes "
    sand_txt = "Sand ski area "

    # try all the prefixes, if one is correct, use it
    try:
        start = h1.index(res_txt) + len(res_txt)
    except ValueError:
        try:
            start = h1.index(in_txt) + len(in_txt)
        except ValueError:
            try:
                start = h1.index(dry_txt) + len(dry_txt)
            except ValueError:
                start = h1.index(sand_txt) + len(sand_txt)


    name = h1[start : ]
    end = name.index("<")
    name = name[ : end ]

    return name

def get_state(resort_file):
    states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','Washington State','West Virginia','Wisconsin','Wyoming']

    soup = BeautifulSoup(resort_file, 'html.parser')

    # check each state name in the html, if it's there, go with it
    for state in states:
        state_html = soup.find_all(string=state)
        if state_html:
            break

    # if a state, isn't found, it's probably California (due to Lake Tahoe weirdness)
    # otherwise, the state is what was found
    if len(state_html) == 0:
        state = 'California'
    else:
        state = state_html[0]

    return state

def write_data(worksheet):
    links_file = open('../skiresorts/skiresort_links', "r")
    website_file = open('../skiresorts/websites', 'r')

    line = links_file.readline()
    website = website_file.readline()

    row = 2
    while line:
        # write the skiresort.info link
        cell = 'A' + str(row)
        worksheet.write(cell, line[ : -1])

        # get the resort file
        last_slash = line.rindex('/')
        link_name = line[last_slash + 1 : -1 ]
        print(link_name)
        
        resort_filename = '../html/skiresorts/' + link_name
        resort_file = open(resort_filename, "r")
        
        # write the resort name
        resort_name = get_name(resort_file)
        cell = 'B' + str(row)
        worksheet.write(cell, resort_name)
        
        resort_file.close()
        
        # write the resort website
        website = website[:-1]
        cell = 'C' + str(row)
        worksheet.write(cell, website)

        # write the resort state
        resort_file = open(resort_filename, "r")

        resort_state = get_state(resort_file)
        cell = 'D' + str(row)
        worksheet.write(cell, resort_state)

        resort_file.close()
        
        # write lat/long
        latlong_file = open('../html/latlongjson/' + link_name, 'r')
        latlong_data = json.load(latlong_file)
        try:
            location = latlong_data['results'][0]['geometry']['location']
            
            lat = location['lat']
            cell = 'E' + str(row)
            worksheet.write(cell, lat)

            lng = location['lng']
            cell = 'F' + str(row)
            worksheet.write(cell, lng)
        except IndexError:
            print(f'no lat/lng for {link_name}')

        # prep for next resort
        row += 1
        line = links_file.readline()
        website = website_file.readline()


    links_file.close()
    website_file.close()

def main():
    # set up workbook
    workbook = Workbook("../../databases/skiresorts.xlsx")
    worksheet = workbook.add_worksheet()

    # set up column names
    worksheet.write('A1', 'skiresort.info link')
    worksheet.write('B1', 'Name')
    worksheet.write('C1', 'Website')
    worksheet.write('D1', 'State')
    worksheet.write('E1', 'Latitude')
    worksheet.write('F1', 'Longitude')

    # fill in the data
    write_data(worksheet)

    workbook.close()
    
if __name__ == "__main__":
    main()

