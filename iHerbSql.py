import requests
from bs4 import BeautifulSoup
import re
import sqlite3

conn = sqlite3.connect('zink.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS iHerb;

CREATE TABLE iHerb (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title    TEXT UNIQUE,
    dosage    TEXT UNIQUE,
    side_effects    TEXT UNIQUE,
    link    TEXT UNIQUE
)
''')


def getTitle(link):
    title = ''
    title1 = link.find('h1', id='name').text
    #to ommit the brand name which appears at the beginning of each title
    title = title1[14:]
    return title

def getDosage(link):
    dosage = ''
    dosage1 = link.find_all('tr')
    for link in dosage1:
        # i don't how to extract differently because there is a multitude of 'td' tags
        if re.search(('Zinc.+mg'), str(link)):
            link = link.find_all('td')
            dosage = link[0].text + ': ' + link[1].text
    return dosage

def getSide_ef(link):
    side_ef = ''
    side_ef1 = link.find_all('div', class_="prodOverviewDetail")
    side_ef = side_ef1[1].text
    return(side_ef)


def scrape(url):

    "Authenticating User-Agent request header"
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    start_link = requests.get(url)
    start_html = start_link.content

    soup = BeautifulSoup(start_html, 'html.parser')
    links = soup.find_all('a', class_='absolute-link product-link')

    for link in links:
        url = link.get('href')
        drug_link = requests.get(url, headers=headers)
        drug_html = drug_link.content
        embedded_link = BeautifulSoup(drug_html, 'html.parser')
        for element in embedded_link:
            title = getTitle(embedded_link)
            dosage = getDosage(embedded_link)
            side_ef = getSide_ef(embedded_link)
            tab_url = url

            cur.execute('''INSERT OR IGNORE INTO iHerb (title, dosage, side_effects, link)
                        VALUES ( ?, ?, ?, ? )''', (title, dosage, side_ef, tab_url))
            conn.commit()


scrape('https://ua.iherb.com/search?sug=zinc&kw=zinc&rank=0&cids=1855&bids=NWY')
