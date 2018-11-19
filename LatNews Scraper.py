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
# load relevant packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os

# use as main function for scraping
def wr_scrape(user, pw, year, loc): 
    
    # provide container vectors       
    titles = []
    bodies = []
    report_n = []
 
    # specify location of Chrome and (opt.) set as headless (silent)
    CHROMEDRIVER_PATH = '/Applications/chromedriver'    
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
    username.send_keys(user)
    password.send_keys(pw)
    
    login_button = driver.find_element_by_name('_eventId_proceed')
    login_button.click()
    
    # go to specific year
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/component/k2/itemlist/category/33.html?archive=true&archive_id=33&update=true")
    year_select = driver.find_element_by_name('period')
    year_select.send_keys(year)
    
    # Selenium hands the page source to Beautiful Soup
    directory_page = BeautifulSoup(driver.page_source, 'lxml')


    # identify all links in relevant section of the page (i.e. only links to stories)
    story_links = []
    for link in directory_page.findAll("a", {"class":"archive_item"}):
        if 'href' in link.attrs:
            link = link.attrs['href']
            story_links.append(link)

    # looping, travel to each link and pull relevant info
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
              
    # Combine output into data.frame
    # combine as columns in dataframe:
    # create lists of labels & values
    list_labels = ['report_n', 'title', 'article_text'] 
    list_values = [report_n, titles, bodies] 

    # zip together labels and values and write a dataframe
    df = pd.DataFrame(dict(list(zip(list_labels, list_values))))
        
    # write to .csv
    os.chdir(loc)
    df.to_csv('articles_' + str(year) + '.csv')
    

# Separate function for pre-2003 PDF versions of report
def pdf_scrape(user, pw, year, loc): 
        
    # specify location of Chrome and (opt.) set as headless (silent)
    CHROMEDRIVER_PATH = '/Applications/chromedriver'    
    chrome_options = Options()  
    #chrome_options.add_argument("--headless")  
    #chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument("--incognito")

    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": loc , "download.extensions_to_open": "applications/pdf"}
    chrome_options.add_experimental_option("prefs", profile)

    # load chrome driver
    driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH,
                              chrome_options=chrome_options)  
    
    # Get content from URL
    driver.implicitly_wait(30)
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/component/k2/itemlist/category/33.html?archive=true&archive_id=33&update=true")
    
    # Enter login information and click submit button
    username = driver.find_element_by_name('j_username')
    password = driver.find_element_by_name('j_password')
    username.send_keys(user)
    password.send_keys(pw)
    
    login_button = driver.find_element_by_name('_eventId_proceed')
    login_button.click()
    
    # go to specific year
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/component/k2/itemlist/category/33.html?archive=true&archive_id=33&update=true")
    year_select = driver.find_element_by_name('period')
    year_select.send_keys(year)
    
    # Selenium hands the page source to Beautiful Soup
    directory_page = BeautifulSoup(driver.page_source, 'lxml')
    
    # identify all links to pdfs
    pdf_links = []
    for link in directory_page.findAll("a", {"target":"_new"}):
        if 'href' in link.attrs:
            link = "https://www-latinnews-com.proxy3.library.mcgill.ca"+link.attrs['href']
            pdf_links.append(link)
    
    # looping through each link and save pdf to loc
    for link in pdf_links:
        driver.get(link)


#--------------------------
# Scraping content
#--------------------------

# Provide user info and directory
my_username = " "
my_password = " "
loc = '/Users/markwilliamson/Documents/RA Work/Corruption/Web scraping'

# scrape html pages
wr_scrape(my_username, my_password, 2013, loc)

# problem years: 2004, 2012

# scrape pre-2003 PDFs
loc = '/Users/markwilliamson/Documents/RA Work/Corruption/Web scraping/Pre-2003 PDFs/'
pdf_scrape(my_username, my_password, 1999, loc)









# ------------------------------------
# Idea for proxy validate function

# function to login into proxy page 
def proxy_validate(user, pw): 
        
    # specify location of Chrome and set as headless (silent)
    CHROMEDRIVER_PATH = '/Applications/chromedriver'    
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
    username.send_keys(user)
    password.send_keys(pw)
    
    login_button = driver.find_element_by_name('_eventId_proceed')
    login_button.click()