import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
import re
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

opts = Options()
# make the driver headless
opts.headless = True
driver = webdriver.Chrome('./chromedriver',options=opts)

# set url of the pages
url = 'https://www.edx.org/search?tab=course'

# use the driver to locate next page button and count how many pages are there
data = []
driver.get(url)
time.sleep(10)
num_pages = int(driver.find_element_by_xpath('//*[@id="displayed-results"]/div[1]/div/nav/ul/li[6]/button').text)
print('Total page: ' + str(num_pages))

# scrape link for each course
for j in range(num_pages):
    print('Page: ' + str(j + 1))
    if j > 0:
        driver.find_element_by_xpath("//*[@id=\"displayed-results\"]/div[1]/div/nav/ul/li[7]/button").click()
        time.sleep(5)
    else:
        time.sleep(0)

    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    summary = soup.find("div",{'static-card-list d-flex m-xl-0 flex-wrap'})
    for i in summary:
        link = [u['href'] for u in i.find_all('a', href=True)]
        data.append([link])
    df = pd.DataFrame(data, columns=['link'])

# clean urls
for i in range(len(df['link'])):
    df['link'][i] = str(df['link'][i]).replace('[','').replace("'",'').replace(']','')
    df['link'][i] = 'https://www.edx.org' + str(df['link'][i])

df.head()

# now scrape data for each course using the list of urls
linksdf = df

url = ''
urls = []

num_pages = len(linksdf['link'])
for i in range(num_pages):
    url_page = linksdf['link'][i]
    urls.append(url_page)

# scrape data for each course
# if the element did not exist, use try/except to avoid errors
data = []
for url in urls:
    print(url)
    driver.get(url)
    time.sleep(3)
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    # title
    try:
        title = soup.title.text
    except:
        title = 'nil'
    
    # author
    try:
        author = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[4]/div[2]/a").text
    except:
        author = 'nil'
    
    # description
    try:
        desc = soup.find('div', {'class': 'course-description'}).findNext('p').text
    except:
        desc = 'nil'
    
    # subject
    try:
        subject = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[5]/div[2]/a").text
    except:
        subject = 'nil'
    
    # price
    try:
        price = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[3]/div[2]/p/span[1]").text
    except:
        price = '0'
    
    # certificate
    try:
        cert = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[3]/div[2]/p/span[2]").text
    except:
        cert = 'nil'
    
    # enrollment
    try:
        enroll = driver.find_element_by_xpath("//*[@id=\"js-number-enrolled-label\"]/span/span").text
    except:
        enroll = 'nil'
    
    # length
    try:
        length = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[1]/div[2]/span").text
    except:
        length = 'nil'
    
    # difficulty
    try:
        diff = driver.find_element_by_xpath("//*[@id=\"main-content\"]/div/div/div/div[1]/div/div[1]/ul/li[6]/div[2]").text
    except:
        diff = 'nil'
    
    # img link
    try:
        img_link = [u['src'] for u in soup.find_all('img', src=True)][1]
    except:
        img_link = 'nil'
    
    data.append([title, author, subject, desc, price, cert, enroll, length, diff, url, img_link])

# create dataframe from scraped data
df = pd.DataFrame(data, columns=['title', 'author', 'subject', 'desc', 'price', 'certificate_price', 'enrollment', 'length', 'difficulty', 'link', 'img_link'])

# delete unneccesary infomation from the table
df['title'] = df['title'].str.replace("edX","")
df['title'] = df['title'].str.replace("|","")

# if the price was free, replace it with 0
df['price'] = df['price'].str.replace("FREE","0")

# export as csv
df.to_csv('edx_courses.csv', sep = ',',encoding='utf-8-sig')
df.head()