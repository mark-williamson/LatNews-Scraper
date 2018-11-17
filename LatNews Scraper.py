#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 08:07:19 2018

@author: markwilliamson
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 11:04:12 2018

@author: markwilliamson
"""

#--------------------------
# Functions
#--------------------------
# use to strip date column correctly 
def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

#--------------------------
# Login
#--------------------------
# load relevant packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# specify location of Chrome and set as headless (silent)
CHROMEDRIVER_PATH = '/Applications/chromedriver'
WINDOW_SIZE = "1920,1080"

chrome_options = Options()  
#chrome_options.add_argument("--headless")  
#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--incognito")


# load chrome driver
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                          chrome_options=chrome_options
                         )  

# Get content from URL
driver.implicitly_wait(30)
driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/component/k2/itemlist/category/33.html?archive=true&archive_id=33&update=true")

# Enter login information and click submit button
username = driver.find_element_by_name('j_username')
password = driver.find_element_by_name('j_password')
username.send_keys(" ")
password.send_keys(" ")

login_button = driver.find_element_by_name('_eventId_proceed')
login_button.click()


#--------------------------
# Scraping content
#--------------------------

from bs4 import BeautifulSoup

# Selenium hands the page source to Beautiful Soup
directory_page = BeautifulSoup(driver.page_source, 'lxml')

# identify all links in relevant section of the page (i.e. only links to stories)
story_links = []
for link in directory_page.findAll("a", {"class":"archive_item"}):
    if 'href' in link.attrs:
        link = link.attrs['href']
        story_links.append(link)

# loop over each link
titles = []
bodies = []
report_n = []
dates = []

for link in story_links:
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/" + link)
    story_page = BeautifulSoup(driver.page_source, 'lxml')
    
    # pull titles
    title = story_page.findAll("h2")
    for h2 in title:
        titles.append(h2.text)
        
    # pull bodies
    body = story_page.findAll("div", {"class":"itemFullText"})
    for div in body:
        bodies.append(div.text)
        
    # pull dates in form of WR title
    date = story_page.findAll("h1")
    for h1 in date:
        report_n.append(h1.text)
        specific_date = find_between(h1.text, "Weekly Report - ", " (" )
        dates.append(specific_date)


# add in the line of code to close the browser after
driver.close()


# ------------------------------------
# working out how to loop years - 2003 is the first year available 
years = range(2003, 2018)
year_select = driver.find_element_by_name('period')

year_select.send_keys(years[1])


for year in years: 
    year_select.send_keys(years[1])

# think I have to convert whole thing above to a function lol....

# ------------------------------------

# ------------------------------------
# Combine output into data.frame
# ------------------------------------
import pandas as pd
import os

# combine as columns in dataframe:
# create lists of labels & values
list_labels = ['date', 'report_n', 'title', 'article_text'] 
list_values = [dates, report_n, titles, bodies] 

# zip together labels and values and write a dataframe
df = pd.DataFrame(dict(list(zip(list_labels, list_values))))

# write to .csv
os.chdir('/Users/markwilliamson/Documents/RA Work/Corruption/Web scraping')
df.to_csv('articles_2018.csv')



# .... for future script:
# ------------------------------------
# Clean extracted text
# ------------------------------------

# most of this just makes sense to do in a separate file rather than at-source: 
# 1. Remove line breaks and whitespace from text using NLTK (e.g. '\n', '\t')
# 2. Identify countries from either title or in-text 
#           named entity recognition for identifying countries: 
#               https://github.com/ushahidi/geograpy
#               https://blog.ouseful.info/2017/09/04/simple-text-analysis-using-python-identifying-named-entities-tagging-fuzzy-string-matching-and-topic-modelling/
# 3. Filter out certain articles? 
#       e.g. based on titles like 'Tracking Trends', 'Leader', 'Quotes of the Week' 
#       ... idk
# 4. Some stories begin with 'COUNTRY NAME |' and this could be removed before analysis















