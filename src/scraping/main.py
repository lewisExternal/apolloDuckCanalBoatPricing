from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import sys
#from webdriver_manager.chrome import ChromeDriverManager
import numpy as np 
import pandas as pd 
import time
import sqlite3
from pyvirtualdisplay import Display

# import scripts 
import getBoatAdverts
import scrapeBoatData
import db_lib

sys.path.append('../src/utils/')
from utils import get_time_stamp

###############################################################
# DATE: 2021/04
# AUTHOR: LEWIS JAMES 
###############################################################

def get_driver():
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    #driver = webdriver.Chrome('./chromedriver')
    # Google VM 
    #chrome_options.binary_location = "/opt/google/chrome/google-chrome"
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    return webdriver.Chrome(options=chrome_options,executable_path=r'/usr/bin/chromedriver')

def main():

    # start of scrape script 
    print( get_time_stamp() + ' - INFO - scraping script has started ')
    
    # create virtual display for Raspberry Pi deployment
    display = Display(visible=0, size=(800, 600))
    display.start()

    # database name 
    database = r"../src/pythonsqlite.db"

    # create the db if it doesn't already exist 
    db_lib.main(database) 
    print("DB called.")
    
    # get connection to db 
    conn = db_lib.create_connection(database)
    print("Connection to the DB established.")

    # ask user, do they want to query for boat auction links 
    # query_boat_links = input("Look for boat links: y/n?")

    # take parameters from the command line 
    arguments = len(sys.argv) - 1
    print ("The script is called with %i argument(s)" % (arguments))

    # first command line argument to look for boats 
    if arguments == 1: 
        query_boat_links = sys.argv[1]
    else: 
        print("Default query_boat_links selected: N ")
        query_boat_links = 'n'

    # get list of boat adverts 
    if query_boat_links.lower() == 'y':
        # start of get links
        print( get_time_stamp() + ' - INFO - get links has started')
        
        links_to_process  =  getBoatAdverts.main()
        print("Link of boat adverts found.")

        # create df for the links 
        links_to_boats_df = pd.DataFrame(links_to_process,columns=['link'])
        links_to_boats_df['processed'] = 0

        # save boat links to DB  
        links_to_boats_df.to_sql('adverts', conn, if_exists='append', index=False)
        print("Boat links have been inserted to the DB.")   
    
        # end of get links
        print( get_time_stamp() + ' - INFO - get links has finished')

    # start of get boat data script 
    print( get_time_stamp() + ' - INFO - get boat data has started')
    
    # get boat data 
    print("Getting boat info from adverts...")
    scrapeBoatData.main(conn)
    
    # end of get boat data script 
    print( get_time_stamp() + ' - INFO - get boat data has finished')

    # end of scrape script 
    print( get_time_stamp() + ' - INFO - scraping script has finished')
    print("Script complete.")

if __name__ == "__main__":
    main()
