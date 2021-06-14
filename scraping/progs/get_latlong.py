'''
    File: get_latlong.py
    Author: Drew Scott
    Description: Retrieves lat/long of all ski resorts using Google geocoding API.
'''

from scrape import scrape

if __name__ == "__main__":
    f = open('../skiresorts/skiresort_links', 'r')

    line = f.readline()
    while line:
        url = 'https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBgNYdMqDp9TRNw0kkilafHpHHsjKjABOo&address='
        
        last_slash = line.rindex('/')
        name = line[last_slash + 1 : -1]

        name_arr = name.split('-')
        for sub in name_arr:
            url += sub + '+'

        url += 'ski+resort'

        scrape(url, 'latlongjson/' + name)

        print(url)

        line = f.readline()

    f.close()
