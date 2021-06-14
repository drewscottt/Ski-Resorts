'''
    File: get_skiresorts_links.py
    Author: Drew Scott
    Description: Retrieves all the links to the individual ski resorts from the skiresort_info file
                 Then writes the links to a new file
'''

from bs4 import BeautifulSoup

if __name__ == "__main__":
    # get all of the divs with individual ski resort links
    html_file = open("../html/skiresort_info", "r")

    soup = BeautifulSoup(html_file, 'html.parser')

    classes = "col-sm-11 col-xs-10"

    resort_divs = soup.find_all("div", {"class": classes})

    html_file.close()

    # get the link from each of the divs
    links = []

    link_ind = 71
    for div in resort_divs:
        div = str(div)
        
        link_start = div[link_ind:]
        quote_ind = link_start.index('"')
        link = link_start[:quote_ind]
      
        links.append(link[:-1])

    # write the links to a file
    f = open("../skiresorts/skiresort_links", "w")
    for link in links:
        f.write(link + "\n")

    f.close()
