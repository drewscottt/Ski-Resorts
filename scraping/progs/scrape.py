'''
    File:
    Author: Drew Scott
    Description: Gets HTML from input URL and saves it to '../html/<specifed filename>'
                 If specified filename already exists, append html to it.
    Arguments:  URL, Filename 
'''

import urllib.request
import sys
import os.path
from os import path

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"


def scrape(URL, filename):
    # get html from specified url
    opener = AppURLopener()
    fp = opener.open(URL)
    html_bytes = fp.read()

    html = html_bytes.decode("utf8")
    fp.close()

    print(html)

    # write to file
    filename = '../html/' + filename
    if not path.exists(filename):
        f = open(filename, "w")
        f.write(html)
        f.close()
    else: 
        f = open(filename, "a")
        f.write(html)
        f.close()


if __name__ == "__main__":
    scrape(sys.argv[1], sys.argv[2])
