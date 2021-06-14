'''
    File: get_tourist_html.py 
    Author: Drew Scott
    Description: Gets html for all of the tourist pages of skiresort.info pages
'''

from scrape import scrape

if __name__ == "__main__":
    links_file = open('../skiresorts/skiresort_links', "r")

    line = links_file.readline()
    while line:
        last_slash = line.rindex('/')
        link_name = line[last_slash + 1 : -1]
        
        print(link_name)

        tourist_link = line[: -1] + '/tourist-info'

        scrape(tourist_link, "tourist_info/" + link_name)

        line = links_file.readline()

    links_file.close()
