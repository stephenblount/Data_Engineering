"""This script will scrape the newest listings of realtor.com
for the seattle area. If those listing do not already existing in 
an SQL database it will append the new listings"""

from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import numpy as np

def fetch_data():

    #Convince Realtor.com that a browser is being directed to Seattle newest listing from google.com
    req_headers = {
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language':'en-US,en;q=0.5',
        'referer':'https://www.google.com/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode':'navigate',
        'sec-fetch-site':'cross-site',
        'sec-fetch-user':'?1',
        'te' : 'trailers',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'
    }


    url = 'https://www.realtor.com/realestateandhomes-search/Seattle_WA/sby-6'
    response = requests.get(url, headers=req_headers)
    
    #Create a soup object of the landing page
    soup = BeautifulSoup(response.text, features="lxml")
    
    #Check the connection was successful
    print(response)


    #Container
    house_list = []

    #Loop through each tile on the landing page and pull and clean key features
    for i in range(42):
        sub_house = []
        
        house = soup.find_all('div', {'data-testid': 'property-detail'})[i]
        price = house.find('span', {'data-label': 'pc-price'})
        beds = house.find('li', {'data-label': 'pc-meta-beds'})
        baths = house.find('li', {'data-label': 'pc-meta-baths'})
        sqft = house.find('li', {'data-label': 'pc-meta-sqft'})
        sqftlot = house.find('li', {'data-label': 'pc-meta-sqftlot'})
        address = house.find('div', {'data-label': 'pc-address'})
        zipcode = house.find('div', {'data-label': 'pc-address-second'})
        
        sub_house.append(int(re.sub(r'[^\d]','', price.text)))
        
        if beds != None:
            beds = beds.text
            if beds == '' or beds == 'Studio':
                sub_house.append(0)
            else:
                sub_house.append(int(re.sub(r'[^\d]','', beds)))
        else:
            sub_house.append(np.nan)
            
        if baths != None:
            sub_house.append(float(re.sub(r'[^\d.]','', baths.text)))
        else:
            sub_house.append(np.nan)
            
        if sqft != None:
            sub_house.append(int(re.sub(r'[^\d]','', sqft.text)))
        else:
            sub_house.append(np.nan)
            
        if sqftlot != None:
            if '.' not in sqftlot:
                sub_house.append(int(re.sub(r'[^\d]','', sqftlot.text)))
            else:
                sub_house.append(int(re.sub(r'[^\d]','', elem[4]))*43560/100)
        else:
            sub_house.append(np.nan)
        
        sub_house.append(address.text)
        
        if zipcode != None:
            sub_house.append(int(re.sub(r'[^\d]','', zipcode.text)))
        else:
            sub_house.append(np.nan)
        house_list.append(sub_house)
        
    #Connect to the SQL Database and insert the new data if the primary key (address) does not exist        
    con = sqlite3.connect('house_price.db')
    cur = con.cursor()
    sql = "INSERT OR IGNORE INTO house VALUES (?, ?, ?, ?, ?, ?, ?)"
    cur.executemany(sql, house_list)
    con.commit()
    con.close()

if __name__ == '__main__':
    fetch_data()
