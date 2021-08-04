# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 21:11:09 2021

@author: Joanna Khek Cuina
"""

import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import requests
from urllib.request import urlopen
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time 
import csv
import os
import sys
from itertools import chain

os.chdir("C:\\Users\\joann\\OneDrive\\Desktop\\NUSWhispers Scrapper")

# setting up options
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

url = "https://nuswhispers.com/latest/"

# chrome browser
driver = webdriver.Chrome("C:\\Users\\joann\\OneDrive\\Desktop\\My Files\\Chrome File\\chromedriver", options=chrome_options)
driver.get(url)
main_window = driver.window_handles[0]


# create empty lists for appending later
ls_category = []
ls_content = []
ls_date = []
ls_reference = []

ls_comments = []
ls_reactions = []
ls_shares = []

def extract_header(header, ls_category):
    for i in range(0, len(header)):
        temp_header = []
        header_words = header[i].find_all("span", class_="ng-binding ng-scope")
        
        for j in range(0, len(header_words)):
            category = header_words[j].getText().replace("\n", "").replace(",", "")
            category = " ".join(category.split())
            temp_header.append(category)
        
        ls_category.append(temp_header)
    
def extract_body(body, ls_content, ls_reference):
    for i in range(0, len(body)):
        body_words = body[i].find_all("span", class_="post-text ng-binding")[0].getText()
        reference_words = body[i].find_all("a", class_="ng-binding")[0].getText()
        
        #ls_content.append(body_words)
        ls_reference.append(reference_words)
        
        
def extract_footer(footer, ls_date):
    for i in range(0, len(footer)):
        footer_words = footer[i].find_all("span", class_="post-time")[0].getText()
        ls_date.append(footer_words)
        
def extract_all():
    
    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
    
        header = soup.find_all("div", class_="post-header")
        body = soup.find_all("div", class_="post-content")
        footer = soup.find_all("div", class_="post-footer")
        
        extract_header(header, ls_category)
        extract_body(body, ls_content, ls_reference)
        extract_footer(footer, ls_date)
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        # scroll to bottom
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        final = pd.DataFrame()
        final["Reference"] = ls_reference
        final["Category"] = ls_category
        #final["Content"] = ls_content
        final["Date"] = ls_date
        
        final = final.drop_duplicates(subset=["Reference", "Date"])
        print("Confessions scraped: {}".format(final.shape[0]))
        final.to_csv("categories.csv", index=0)
        
        if (new_height == last_height):
            print("End of page")
            break
        
        

extract_all() 

        
    
    
        