from selenium import webdriver
from web_driver_setup import Web_Driver_Setup
from selenium.webdriver.common.by import By
import json 
import time

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

# Customize options for web driver 
chrome_options = webdriver.ChromeOptions()
# make browder window invisible
chrome_options.add_argument("--headless=new")  
# https://developer.mozilla.org/en-US/docs/Glossary/User_agent
chrome_options.add_argument(f"--user-agent={user_agent}")  

# Initialize the WebDriver
webdriver_setup = Web_Driver_Setup(options = chrome_options)
driver = webdriver_setup.initialize_driver()

target_url = "https://twitter.com/scrapingdog"
driver.get(target_url)
# make sure to iclude this so that the webpage can load before
# you try to scrape it
time.sleep(2)
resp = driver.page_source

l = list()
o = {}

o["profile_name"] = driver \
                        .find_element(By.TAG_NAME, 'main') \
                        .find_element(By.XPATH, "div/div/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div[1]/div/div/span/span[1]") \
                        .text

o["profile_handle"] = driver \
                        .find_element(By.TAG_NAME, 'main') \
                        .find_element(By.XPATH, 'div/div/div/div/div/div[3]/div/div/div/div/div[2]/div/div/div[2]/div/div/div/span') \
                        .text

try:
    o["profile_bio"] = driver \
                        .find_element(By.TAG_NAME, 'main') \
                        .find_element(By.XPATH, 'div/div/div/div/div/div[3]/div/div/div/div/div[3]/div/div/span') \
                        .text
except:
    o["profile_bio"] = None

print(o["profile_name"])
print(o["profile_handle"])
print()
driver.close()
