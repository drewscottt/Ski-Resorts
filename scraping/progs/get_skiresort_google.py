'''
    File: get_skiresort_google.py
    Author: Drew Scott
    Description: Gets the Google search page for each ski resort
'''

from scrape import scrape
if __name__ == "__main__":
    f = open('../skiresorts/skiresort_links', 'r')
    
    line = f.readline()

    while line:
        url = 'https://www.google.com/search?q='
        
        last_slash = line.rindex('/')
        name = line[ last_slash + 1 : -1 ]

        name_arr = name.split('-')
        for sub in name_arr:
            url += sub + '+'

        url += 'ski+resort'

        print(url)
        scrape(url, 'google/' + name)

        line = f.readline()

    f.close()
