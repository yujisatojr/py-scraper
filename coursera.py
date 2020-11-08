import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

# Free Courses on Coursera
url = 'https://www.coursera.org/courses?query=free'
 
result = requests.get(url)
c = result.content
soup = BeautifulSoup(c, "html.parser")

urls = []
urls.append(url)

# get url for each page
num_pages = 50
for i in range(num_pages-1):
    pg = str(i+2)
    url_page = url + '&page=' + pg + '&index=prod_all_products_term_optimization'
    urls.append(url_page)

# scrape for each url
data = []
for url in urls:
    print(url)
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, "html.parser")
    summary = soup.find("ul",{'ais-InfiniteHits-list'})
    items = summary.find_all('li', class_ = 'ais-InfiniteHits-item')
    for i in items:
        # items
        name = ''
        author = ''
        rating = 0.0
        enroll = ''
        diff = ''
        link = ''
        
        #get values
        name = i.find_all('div', class_ = 'horizontal-box')[0].string
        author = i.find_all('div', class_ = 'horizontal-box')[1].string
        if i.find('span', 'ratings-text') is None:
            rating = 0
        else:
            rating = i.find_all('span', 'ratings-text')[0].string
            
        if i.find('span', 'enrollment-number') is None:
            enroll = 'N/A'
        else:
            enroll = i.find_all('span', 'enrollment-number')[0].string
        diff = i.find_all('span', 'difficulty')[0].string
        
        category = i.find_all('div', '_jen3vs _1d8rgfy3')[0].string
        
        tag = i.find_all('div')[0]
        link = [u['href'] for u in tag.find_all('a', href=True)]
            
        data.append([name, author, rating, enroll, category, diff, link])
    # give one second break after scraping each page
    time.sleep(1)
df = pd.DataFrame(data, columns=['name', 'author', 'rating', 'enrollment', 'type', 'difficulty', 'link'])

# data cleansing
for i in range(len(df['enrollment'])):
    if "." in df['enrollment'][i]:
        df['enrollment'][i] = str(df['enrollment'][i]).replace('.','')
        df['enrollment'][i] = str(df['enrollment'][i]).replace('k','000').replace('m','00000')
    else:
        df['enrollment'][i] = str(df['enrollment'][i]).replace('k','000').replace('m','00000')
        
    df['difficulty'][i] = df['difficulty'][i].lower()
    df['type'][i] = df['type'][i].lower()

for i in range(len(df['link'])):
    df['link'][i] = df['link'][i][0]
    df['link'][i] = str(df['link'][i]).replace('[','').replace("'",'').replace(']','')
    df['link'][i] = 'https://www.coursera.org' + str(df['link'][i])

# export dataframe as csv
df.to_csv('coursera_free_all.csv', sep = ',',encoding='utf-8-sig')
df.head()