'''
    File: get_skiresorts_html.py
    Author: Drew Scott
    Description: Reads through all of the links in '../skiresorts/skiresorts_links' and scrapes them
                 Uses the scrape function from scrape.py to add them to '../html/skiresorts/<name of resort>'
'''


from scrape import scrape


if __name__ == "__main__":
    f = open("../skiresorts/skiresort_links", "r")

    line = f.readline()
    while line:
        last_slash = line.rindex("/") 
        name = line[last_slash + 1 : -1]
        print(name)

        
        scrape(line, "skiresorts/"+name)
        
        line = f.readline()

    f.close()
