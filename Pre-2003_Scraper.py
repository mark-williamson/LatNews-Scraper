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
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
import re
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC


    # -----------------    
    # 1. Initiate browser and enter proxy credentials
    # -----------------
    
    # specify location of Chrome and (opt.) set as headless (silent)
CHROMEDRIVER_PATH = '/Applications/chromedriver'    
chrome_options = Options()  
    #chrome_options.add_argument("--headless")  
    #chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.add_argument("--incognito")

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


    #   get cookie consent window removed
driver.implicitly_wait(120)
driver.find_element_by_xpath("//*[@aria-label='dismiss cookie message']").click()
                

def pre2003_scrape(search, date1, date2, loc): 
    
    # -----------------
    # 2. Execute search
    # -----------------
    
    driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/search.html#")
    
    #   select only WR reports -- this is kinda janky w/ the [1] but not sure how else to directly select the correct checkbox otherwise
    buttons = [str(num) for num in [3, 38, 25, 26, 28, 40, 74, 8, 7, 6, 11]]
    driver.implicitly_wait(1000)
    for button in range(0,len(buttons)):
        driver.find_elements(By.XPATH, "//*[(@value='"+buttons[button]+"')]")[1].click()

    #   input search query (search arg is a string provided to function)
    driver.find_element_by_id("txtSearch").send_keys(search)
    

    #   set date range - change this code if input is str not datetime
    # date1 = datetime.strptime(date1, "%d/%m/%Y")
    # date2 = datetime.strptime(date2, "%d/%m/%Y")
    
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

    # Selenium hands the page source to Beautiful Soup
    driver.implicitly_wait(30)
    search_results_page = BeautifulSoup(driver.page_source, 'lxml')
    
    # identify all links in relevant section of the page (i.e. only links to stories)
    story_links = []
    link_regex = re.compile('.*archive_item searchlist.*')
    for link in search_results_page.findAll("a", {"class":link_regex}):
        if 'href' in link.attrs:
            link = link.attrs['href']
            story_links.append(link)
    
    # provide container vectors
    titles = []
    bodies = []
    report_n = []           

    # looping, travel to each link and pull relevant info
    for link in story_links:
        driver.get("https://www-latinnews-com.proxy3.library.mcgill.ca/" + link)
        story_page = BeautifulSoup(driver.page_source, 'lxml')
            
        # pull dates in form of WR title -- WORKING
        date = story_page.find_all("h2", string=re.compile("Weekly Report"))
        for h2 in date:
                report_n.append(h2.text)
                   
        # pull titles
        title = story_page.find_all("h3")
        title_text = []
        for title in title:
            title_text.append(title.text)
        
        # this join addresses cases of 'multiple' titles
        title_text = " - ".join(title_text)
        titles.append(title_text)
            
        # pull bodies
        for para in story_page.find_all("div", {"class":"col-lg-12 main-content-area"}):
            
            # this gets a ton of text that isn't wanted, will need to slice away unwanted
            all_text = para.get_text(separator=' ')
            
            # cut out 'return to top' at end of string
            if all_text.endswith('Return to top'):
                all_text = all_text[:-14]
            else:
                all_text = all_text
            
            # find date again and attach to other header element
            header = ["Latinnews Archive " + h2.text + " " for h2 in story_page.find_all("h2", string=re.compile("Weekly Report"))]
            
            # remove date, header info from all_text
            all_text = all_text.split(header[0])[-1]
            
            # repeat for title text
            title = [title.text + " " for title in story_page.findAll("h3")]
            all_text = all_text.split(title[0])[-1]
            
            bodies.append(all_text)
                
    # -----------------
    # 3. Combine output into data.frame
    # -----------------
    
    # combine as columns in dataframe:
    # create lists of labels & values
    list_labels = ['report_n', 'title', 'article_text'] 
    list_values = [report_n, titles, bodies] 

    # zip together labels and values and write a dataframe
    df = pd.DataFrame(dict(list(zip(list_labels, list_values))))
        
    # write to .csv
    os.chdir(loc)
    df.to_csv('articles_' + str(date1)[:10] + '_' + str(date2)[:10] + '.csv')


# actual search
my_username = ""
my_password = ""
search = "Latin America OR Argentina OR Bahamas OR Barbados OR Belize OR Bolivia OR Brazil OR Chile OR Colombia OR Costa Rica OR Cuba OR Dominican Republic OR Ecuador OR El Salvador OR Guatemala OR Guyana OR Haiti OR Honduras OR Jamaica OR Mexico OR Nicaragua OR Panama OR Paraguay OR Peru OR Suriname OR Trinidad OR Uruguay OR Venezuela"
loc = '/Users/markwilliamson/Documents/RA Work/Corruption/Web scraping/Pre-2003'


# Create start and end date lists to iterate over 

def return_dates(year):
    
    # define first day as January 1
    date1 = datetime.strptime("1/1/" + str(year), "%d/%m/%Y")

    # Add 14 days repeatedly from Jan 1
    start_dates = pd.date_range(start = date1, periods = 26, freq = '14D')
    
    # define end of each period as 13 days after start period
    end_dates = list(start_dates + pd.DateOffset(days=13))
    
    # replace whatever last end period is with last day of year
    end_dates[-1] = pd.Timestamp(year = year, month = 12, day = 31)

    # convert start dates to list
    start_dates = list(start_dates)
    
    return(start_dates, end_dates)

start_dates, end_dates = return_dates(2002)


# Loop over dates and run scraper on each 
for date in range(0,len(start_dates)+1): 
    pre2003_scrape(search, start_dates[date], end_dates[date], loc)


'''
problem: search box is limited to 250 characters. 

 I think we'll need to write a loop that searches sections of this string for 
 the given dates and then appends them if they're not already found by the earlier 
 part of the search(es)?? fuck that's a disaster 

full search:  
Latin America OR Argentina OR Bahamas OR Barbados OR Belize OR Bolivia OR Brazil OR Chile OR Colombia OR Costa Rica OR Cuba OR Dominican Republic OR Ecuador OR El Salvador OR Guatemala OR Guyana OR Haiti OR Honduras OR Jamaica OR Mexico OR Nicaragua OR Panama OR Paraguay OR Peru OR Suriname OR Trinidad & Tobago OR Uruguay OR Venezuela OR economy OR politics OR party OR election OR finance OR corruption OR country OR island OR minister OR military OR war OR polls OR vote OR buy OR trade OR speech OR resources OR public OR company OR protest OR budget OR government OR unemployment OR market OR economic OR political OR poll OR violence OR court OR prosecution OR international OR tax OR social OR power    

'''




