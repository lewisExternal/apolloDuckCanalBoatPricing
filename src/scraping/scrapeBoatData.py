from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import sys
from time import sleep
#from webdriver_manager.chrome import ChromeDriverManager
import numpy as np 
import pandas as pd 
import db_lib

def get_driver():
    
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless")
    # Google VM 
    #chrome_options.binary_location = "/opt/google/chrome/google-chrome"
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=chrome_options,executable_path=r'/usr/bin/chromedriver')

def cycle_boat_adverts(boat_links,conn):
        # keep track of progress 
        counter = 1
        total  = len(boat_links)

        for link in boat_links:
            try: 
                # get driver 
                driver = get_driver()
                # convert to a string 
                link = ''.join(link)
                print("Processing "  + str(counter) + "/" + str(total)  +  ": "  + link)
                # get boat advert  
                driver.get(link)
                # scrape data 
                boat_data = [link,get_price(driver),get_status(driver),get_desc(driver),get_specs(driver),get_dealer(driver),get_title(driver),get_location(driver)]
                # convert to dataframe 
                df = pd.DataFrame(data=[boat_data], columns=["link","price","status","desc","specs","dealer","title","location"])
                # insert into the database if valid 
                if df['specs'].iloc[0] != 'Error':
                    df.to_sql('boats', conn, if_exists='append', index=False)
                    db_lib.update_processed_boat(conn,link)      
            except Exception as e:
                print("An error has occurred: "+ str(e))
            finally: 
                driver.close()
                counter = counter + 1 
        

def get_price(driver,attempts=3):
    
    for attempt in range(attempts):
        try:
            price = driver.find_element_by_id('nativePrice')
            price = price.text
            price = (price.replace(" ", "")).replace("|","") 
            return price
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)

    return 'Error'

def get_status(driver,attempts=3):

    for attempt in range(attempts):
        try:
            status = driver.find_elements_by_class_name('_pclData')[1]
            status = status.text
            return status
        
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)
    
    return 'Error'

def get_desc(driver,attempts=3):

    for attempt in range(attempts):
        try:
            desc = driver.find_elements_by_class_name('advert')[0].find_elements_by_tag_name('p')[4] 
            desc = desc.text     
            return desc
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)

    return 'Error'

def get_specs(driver,attempts=3):

    for attempt in range(attempts):
        try:
            specs = driver.find_elements_by_class_name('featureSpecifications')[0].find_elements_by_tag_name('tbody')[0] 
            specs = specs.text          
            return specs
        
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)           

    return 'Error'

def get_dealer(driver,attempts=3):

    for attempt in range(attempts):
        try:
            dealer = driver.find_elements_by_class_name('advert')[0].find_elements_by_class_name('_dealerContactLabel')[0] 
            dealer = dealer.text          
            return dealer
        
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)

    return 'Error' 

def get_title(driver,attempts=3):

    for attempt in range(attempts):
        try:
            title = driver.find_elements_by_class_name('advert')[0].find_elements_by_class_name('_boatAdvertTitle')[0] 
            title = title.text          
            return title
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)

    return 'Error' 

def get_location(driver,attempts=3):

    for attempt in range(attempts):
        try:
            location = driver.find_elements_by_id('contactSection')[0].find_element_by_class_name('_pcl').find_element_by_tag_name('tbody')
            location = location.text          
            location = location.split('UK\n[View Map]')[0]
            location = location.split(' ')
            length  = len(location)
            location = location[length-2]
            return location
        except Exception as e:
            print(str(e))
            driver.refresh()
            sleep(2)

    return 'Error' 


def main(conn):

    # get boat links from the DB 
    boat_links = db_lib.get_boat_links_to_process(conn)
    
    # cycle through the links 
    print("Get boat data...")
    cycle_boat_adverts(boat_links,conn)
    
if __name__ == "__main__":
    main()

