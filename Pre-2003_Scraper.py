#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  1 11:11:09 2018

@author: markwilliamson
"""

# load relevant packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

def pre2003_scrape(user, pw): 
    
    # -----------------    
    # 1. Initiate browser and enter proxy credentials
    # -----------------
    
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
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/search.html#")
    
    # Enter login information and click submit button
    username = driver.find_element_by_name('j_username')
    password = driver.find_element_by_name('j_password')
    username.send_keys(my_username)
    password.send_keys(my_password)
    
    login_button = driver.find_element_by_name('_eventId_proceed')
    login_button.click()
    
    # -----------------
    # 2. Execute search
    # -----------------
    
    #   get cookie consent window removed
    driver.implicitly_wait(30)
    driver.find_element_by_xpath("//*[@aria-label='dismiss cookie message']").click()
    
    #   click button to uncheck all report boxes
    driver.implicitly_wait(30)
    invert_sel_button = driver.find_element_by_id("invertselectsearchlink")
    invert_sel_button.click()
            
    #   select only WR reports -- this is kinda janky w/ the [1] but not sure how else to directly select the correct checkbox otherwise
    driver.find_elements(By.XPATH, "//*[(@value='33')]")[1].click()

    #   input search query (search arg is a string provided to function)
    driver.find_element_by_id("txtSearch").send_keys(search)
    

    #   set date range
    #       these will be user-provided later
    date1 = "1/1/2003" 
    date2 = "31/1/2003"
    #       this will remain in function
    date1 = datetime.strptime(date1, "%d/%m/%Y")
    date2 = datetime.strptime(date2, "%d/%m/%Y")
    
    #   input start dates
    oSelect = Select(driver.find_element_by_id("cmbFromDay"))
    oSelect.select_by_visible_text(str(date1.day))

    oSelect = Select(driver.find_element_by_id("cmbFromMonth"))
    oSelect.select_by_visible_text(str(date1.strftime("%b")))

    oSelect = Select(driver.find_element_by_id("cmbFromYear"))
    oSelect.select_by_visible_text(str(date1.year))

    #   input end dates
    oSelect = Select(driver.find_element_by_id("cmbToDay"))
    oSelect.select_by_visible_text(str(date2.day))

    oSelect = Select(driver.find_element_by_id("cmbToMonth"))
    oSelect.select_by_visible_text(str(date2.strftime("%b")))

    oSelect = Select(driver.find_element_by_id("cmbToYear"))
    oSelect.select_by_visible_text(str(date2.year))

    #   click search - again, not ideal to select index from list, but working for now
    driver.find_elements(By.NAME, "Submit")[1].click()
  
    # -----------------
    # 3. Extract article content 
    # -----------------

# Return to problem here

    # Selenium hands the page source to Beautiful Soup
    search_results_page = BeautifulSoup(driver.page_source, 'lxml')
    
    # provide container vectors       d
    titles = []
    bodies = []
    report_n = []
    
    
    for bullet in search_results_page.findAll("li", )

    # identify all links in relevant section of the page (i.e. only links to stories)
    story_links = []
    for link in search_results_page.findAll("a", {"class":"archive_item searchlist_a3"}):
        if 'href' in link.attrs:
            link = link.attrs['href']
            story_links.append(link)
            

    # looping, travel to each link and pull relevant info
    for link in story_links:
        driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/" + link)
        story_page = BeautifulSoup(driver.page_source, 'lxml')
            
        # pull titles
        title = story_page.findAll("h3")
        for title in title:
            titles.append(title.text)
                
        # pull bodies
        body = story_page.findAll("b", {"class":"col-lg-12 main-content-area"})
        for article in body:
            bodies.append(article.text)
                
        # pull dates in form of WR title
        date = story_page.findAll("h2", {"style":"margin-bottom: 15px; font-size: 36px"})
        for h2 in date:
                report_n.append(h2.text)
                

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



# actual search
my_username = ""
my_password = ""
search = "Argentina OR Bahamas OR Barbados OR Belize OR Bolivia OR Brazil OR Chile OR Colombia OR Costa Rica OR Cuba OR Dominican Republic OR Ecuador OR El Salvador OR Guatemala OR Guyana OR Haiti OR Honduras OR Jamaica OR Mexico OR Nicaragua OR Panama OR Paraguay OR Peru OR Suriname OR Trinidad & Tobago OR Uruguay OR Venezuela"
loc = '/Users/markwilliamson/Documents/RA Work/Corruption/Web scraping/Pre-2003'

