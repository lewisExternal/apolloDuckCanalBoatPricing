from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import sys
#from webdriver_manager.chrome import ChromeDriverManager
import numpy as np 
import pandas as pd 


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

def calculate_upper_limit(final_page_no):
    try:
        upper_limit = ( final_page_no - 1 ) * 10 
        
        return upper_limit
    except:
        return 'Error'

def get_final_page(driver):
    try:
        page_element = driver.find_elements_by_xpath('//*[@id="_contentArea"]/div[5]/div/span[1]')[0]
        final_page_no = int(page_element.text)
        return final_page_no
    except:
        return 'Error'  

def get_boat_adverts(driver):
    try:
        page_elements = driver.find_elements_by_class_name('_FeatureTitle')
        return page_elements
    except Exception as e:
        return 'Error'+ str(e)  

def cycle_pages(driver,upper_limit,result_array,attempts=3):
    for page in range(0,upper_limit,10):
        
        for attempt in range(attempts):

            try: 
                driver.get("https://narrowboats.apolloduck.co.uk/boats-for-sale?next="+str(page)+"&sort=0&fx=GBP&limit=10")
                # get boat links 
                page_element = get_boat_adverts(driver)
                # extract urls of boat adverts 
                result_array = extract_boat_links(page_element,result_array)
                print("The following has been processed: " + "https://narrowboats.apolloduck.co.uk/boats-for-sale?next="+str(page)+"&sort=0&fx=GBP&limit=10" )
                break
            except Exception as e :
                print('An error has occured with: ' + str(page)+ str(e))
                driver.close()
                driver = get_driver()

    
    return result_array


def extract_boat_links(get_boat_adverts,result_array):
    for element in get_boat_adverts: 
            # Append link to the array 
            href = element.get_attribute("href")
            result_array.append(href)
    return result_array

def main():

    # get driver 
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = get_driver()

    # set array for results 
    result_array = []
    
    # get boats listed for sale 
    driver.get("https://narrowboats.apolloduck.co.uk/boats-for-sale")

    # get final page number 
    final_page_no = get_final_page(driver)
    print("Final page: " + str(final_page_no))

    # find the upper limit of the auction pages  
    upper_limit = calculate_upper_limit(final_page_no)
    print("Upper limit: "+str(upper_limit))

    # cycle through pages to get boat urls 10 at a time 
    result_array = cycle_pages(driver,upper_limit,result_array)

    return result_array

if __name__ == "__main__":
    main()

