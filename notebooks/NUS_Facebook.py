# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 14:32:02 2021

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
from pandas.core.common import flatten

os.chdir("C:\\Users\\joann\\OneDrive\\Desktop\\My Files\\Github\\NUSWhispers Scrapper")

# setting up options
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

# main url
url = "https://www.facebook.com"

# chrome browser
print("Opening Chrome Browser...")
driver = webdriver.Chrome("C:\\Users\\joann\\OneDrive\\Desktop\\My Files\\Chrome File\\chromedriver", options=chrome_options)
driver.get(url)
main_window = driver.window_handles[0]

# login details
print("Logging in...")
time.sleep(1)
soup = BeautifulSoup(driver.page_source, "html.parser")
               
inputElement = driver.find_element_by_id("email")
inputElement.send_keys(os.environ.get("FACEBOOK_USER"))

inputElement = driver.find_element_by_id("pass")
inputElement.send_keys(os.environ.get("FACEBOOK_PASSWORD"))

driver.find_elements_by_css_selector("button[type*='submit']")[0].click()
time.sleep(1)
            
# navigate to NUS whispers page
print("NUSWhispers Page...")
driver.get("https://www.facebook.com/nuswhispers/")   
time.sleep(1)    
  
# scrape details
ls_content = []
ls_reference = []

ls_comment = []
ls_reaction = []
ls_share = []   
         

def extract_details(start_num, last_num, first_table, see_more, ls_content, ls_reference, ls_comment, ls_reaction, ls_share):
     
    for i in range(start_num, len(first_table)):
    
        reaction_status = "Yes"
        comments_status = "Yes"
        print("Length of first table {}".format(len(first_table)))
        
        # get last table number
        last_num[0] = len(first_table)
        print("Last_num: {}".format(last_num))
    
        try:
            body_table = first_table[i].find_all("div", class_="ecm0bbzt hv4rvrfc dati1w0a e5nlhep0")[0]
        except:
            # non-text confessions
            print("Error in body table. Skipping Iteration")
            continue
        
        try:
            reaction_table = first_table[i].find_all("span", class_="du4w35lb")[0].find_all("span", class_="t0qjyqq4 jos75b7i j6sty90h kv0toi1t q9uorilb hm271qws ov9facns")
        except:
            print("Reaction Status: No")
            reaction_status = "No"
            
        try:
            comments_table = first_table[i].find_all("span", class_="d2edcug0 hpfvmrgz qv66sw1b c1et5uql lr9zc1uh a8c37x1j fe6kdd0r mau55g9w c8b282yb keod5gw0 nxhoafnm aigsh9s9 d3f4x2em iv3no6db jq4qci2q a3bd9o3v b1v8xokw m9osqain")
        except:
            print("Comment Status: No")
            comments_status = "No"
            
            
        # reactions
        reaction_temp = []
        if (reaction_status == "Yes"):
            for j in range(0, len(reaction_table)):
                reaction_num = reaction_table[j].find_all("div", role="button")[0]["aria-label"]
                reaction_temp.append(reaction_num)
        else:
            reaction_temp.append("No Reactions")
            
        # comments
        if (comments_status == "Yes"):   
            # comments and shares
            if (len(comments_table) == 2):
                comments_num = comments_table[0].getText()
                shares_num = comments_table[1].getText()
            elif (len(comments_table) == 1):
                comments_num = comments_table[0].getText()
                if ("Comments" not in comments_num):
                    shares_num = comments_num
                    comments_num = "0 Comments"
                else:
                    comments_num = comments_num
                    shares_num = "0 Shares"
            else:
                comments_num = "0 Comments"
                shares_num = "0 Shares"
        else:
            comments_num = "0 Comments"
            shares_num = "0 Shares"
        
        try:
            driver.find_elements_by_css_selector(see_more)[1].click()
            driver.find_elements_by_css_selector(see_more)[1].click()
        except:
            print("Unable to find see more options")
    
        soup = BeautifulSoup(driver.page_source, "html.parser")
        second_table = soup.find_all("div", class_="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0")
        print("Length of second table: {}".format(len(second_table)))
        
        body_table = second_table[i].find_all("div", class_="ecm0bbzt hv4rvrfc dati1w0a e5nlhep0")[0]
        
        content_words = body_table.find_all("div", class_="j83agx80 cbu4d94t ew0dbk1b irj2b8pg")[0].getText()
        try:
            reference_words = re.search('-#(.*)https://', content_words).group(1).replace(": ", "")
        except:
            reference_words = re.search('#(.*):', content_words).group(1)
            
        print("#{}".format(reference_words))
        print("Reactions: {}".format(reaction_temp))
        print("Comments: {}".format(comments_num))
        print("Shares: {}".format(shares_num))
        
        ls_content.append(content_words)
        ls_reference.append(reference_words)
        ls_reaction.append(reaction_temp)
        ls_comment.append(comments_num)
        ls_share.append(shares_num)
        
        # write into dataframe
        final = pd.DataFrame()
        final["Reference"] = ls_reference
        final["Content"] = ls_content
        final["Reaction"] = ls_reaction
        final["Comment"] = ls_comment
        final["Share"] = ls_share
        
        # remove duplicates
        final = final.drop_duplicates(subset="Reference")
        print("Confessions Scraped: {}".format(final.shape[0]))
        print("========================")
        final.to_csv("final.csv", index=0)
    

####################################################################
soup = BeautifulSoup(driver.page_source, "html.parser")
count = 1
last_num = [0]

print("Executing 'See More'")
see_more = "div[class*='oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gpro0wi8 oo9gr5id lrazzd5p']"
driver.find_elements_by_css_selector(see_more)[1].click()
    
while True:
    
    soup = BeautifulSoup(driver.page_source, "html.parser")

    first_table =  soup.find_all("div", class_="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0")
    
    if (count == 1):
        start_num = 0
    else:
        start_num = last_num[0]
        
    print("=========================")
    print("Starting Number: {}".format(start_num))
    print("Length of table: {}".format(len(first_table)))
    
    extract_details(start_num, last_num, first_table, see_more, ls_content, ls_reference, ls_comment, ls_reaction, ls_share)
    count += 1