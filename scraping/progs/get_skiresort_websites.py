'''
    File: get_skiresort_websites.py
    Author: Drew Scott
    Description: Reads ../html/google/<ski resort> to find the website for the ski resort (the first search result link)
'''

def next_link(html, count):
    sub = 'http'
    for i in range(count):
        sub_ind = html.index(sub)
        html = html[sub_ind + len(sub) : ]

    return html

if __name__ == "__main__":
    f = open('../skiresorts/skiresort_links', 'r')
    line = f.readline()

    websites_file = open('../skiresorts/websites', 'w')

    while line:
        last_slash = line.rindex('/')
        name = line[last_slash + 1 : -1]

        google_html_file = open('../html/google/' + name, 'r')
        google_html = google_html_file.read()
        google_html_file.close()

        google_html = next_link(google_html, 3)

        and_ind = google_html.index('&')
        website = 'http' + google_html[ : and_ind]
        isGood = False

        bad_sites = ['google', 'youtube', 'facebook', 'skiresort.info', 'wikipedia', 'tripadvisor', 'squarespace', 'choicehotels', 'skicentral']

        while not isGood:
            isGood = True
            for site in bad_sites:
                if site in website:
                    isGood = False

                    google_html = next_link(google_html, 1)                    

                    and_ind = google_html.index('&')
                    website = 'http' + google_html[ : and_ind]
    

        websites_file.write(website + '\n')

        line = f.readline()

    f.close()
    websites_file.close()


