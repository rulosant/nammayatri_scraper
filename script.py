from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import csv

import time
import datetime

import os 
import random

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.action_chains import ActionChains

import logging

random_time_min = 3
random_time_max = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
) # + info: https://realpython.com/python-logging/#using-handlers


def sleep_custom(sleep_time):
    if sleep_time >= 1: 
        logging.info("Sleep %ss", str(sleep_time))
    time.sleep(sleep_time)

def random_sleep():
    global random_time_min
    global random_time_max
    delay = random.randint(random_time_min,random_time_max)
    #print("Sleep " + str(delay) + "s")
    logging.info("Sleep %ss (random)", str(delay))
    time.sleep(delay)

def save_csv_terms_from_dict(areas_list):
    filename = "".join(['export\ward_list.csv'])
    with open(filename, 'w', newline='', encoding="utf-8") as csvfile:
        wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL, quotechar='"')
        # Strips the newline character
        wr.writerow(["ward", "status"])
        for term in areas_list:
            wr.writerow([term['ward'], term['status']]) 


def run_search(driver):
    global start_time
    logging.info("run_search()")
    
    driver.get("https://nammayatri.in/open/")
    #sleep_custom(5)
    
    
    # Area
    SHORT_TIMEOUT = 30
    WebDriverWait(driver, SHORT_TIMEOUT
        ).until(EC.presence_of_element_located((By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/div')))

    logging.info("Clicking Area Select...")
    div_area = driver.find_element(By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/div')
    #sleep_custom(2)
    div_area.click()
    sleep_custom(2)
    
    area_options = driver.find_elements(By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[2]/div[2]/div[1]/div/div/div[2]/div/div[2]/div')
    
    logging.info("Reading areas...")
    areas_str=[]
    areas_list=[]
    for area in area_options:
        areas_str.append(area.text)

        term = {"ward": area.text, "status": 'Pending'}
        #print(term) 
        areas_list.append(term)        

  
    save_csv_terms_from_dict(areas_list)

    current_time = datetime.datetime.now()
    logging.info('elapsed time: {}'.format(current_time - start_time)) 
        
    logging.info("Areas detected: {}".format(len(areas_str)))
        
    actions = ActionChains(driver)
    actions.move_to_element(div_area).perform()
    
    current_number = 1
    #for area_str in areas_str:
    for term in areas_list:
        area_str = term['ward']
        logging.info('Current: {}: {}'.format(current_number,area_str))
        sleep_custom(1)

        try:
            logging.debug('Area Click')
            driver.find_element(By.XPATH, "//span[text()='{}']".format(area_str)).click()
            
            # Trend download
            logging.info('Trend download')
            #sleep_custom(2)
            download_button = driver.find_element(By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[4]/div[2]/button/div/div')
            download_button.click()
            
            # Expand
            if driver.find_elements(By.XPATH, "//span[text()='More Trends']"):
                logging.info('Expand')
                #more_button = driver.find_element(By.XPATH, "//span[text()='More Trends']").click()
                more_button = driver.find_element(By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[1]/div[4]/div[1]/div/span')
                more_button.click()
                sleep_custom(2)
                
            #sleep_custom(2)
            
            # Conversion download
            logging.info('Conversion download')
            download_button_conversion = driver.find_element(By.XPATH, '/html/body/astro-island/div/div/div[2]/div[2]/div/div[2]/div[4]/div/div[2]/div/div[4]/div[2]/button/div/div')
            download_button_conversion.click()

            term['status']='Ready'
            save_csv_terms_from_dict(areas_list)
        except:
            term['status']='Failed'
            save_csv_terms_from_dict(areas_list)

        current_time = datetime.datetime.now()
        logging.info('elapsed time: {}'.format(current_time - start_time)) 
        
        logging.debug('moving to Trend Div')
        sleep_custom(1)

        logging.info("Clicking Area Select...")
        actions.move_to_element(div_area).perform()
        div_area.click()
        sleep_custom(1)   
        
        current_number = current_number+ 1


cwd = os.getcwd()
path = cwd + "\export"
logging.info('Path is set to: %s', path)

if not os.path.exists(path):
    os.mkdir(path)
    
    logging.info("Folder %s created!" % path)


chromeOptions = Options()
chromeOptions.add_argument('--headless=new')

chromeOptions.add_experimental_option("prefs", {
        "download.default_directory": "{}".format(path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
})
#chromeOptions.add_experimental_option("prefs",prefs)
#driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

driver = webdriver.Chrome(options=chromeOptions)



start_time = datetime.datetime.now()
logging.info(start_time) 

run_search(driver)

end_time = datetime.datetime.now()
logging.info("Finished")
logging.info(end_time) 
logging.info(end_time - start_time) 



#menu(driver)