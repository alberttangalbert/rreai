from selenium import webdriver
from web_driver_setup import Web_Driver_Setup
from scrapers import Reddit_Scraper
import json 

# Example usage
if __name__ == "__main__":
    #to get your own local user agent 
    #literally jst search up "how to get user agent from browser"
    #in google and the first thing that will pop up is a section "Your user agent"
    #for the future when we have rotating proxies in a for-loop 
    #we will continuously rotate the user_agent
    #https://stackoverflow.com/questions/56889999/how-to-rotate-proxies-and-user-agents
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

    # Customize options for web driver 
    chrome_options = webdriver.ChromeOptions()
    # make brower window invisible
    chrome_options.add_argument("--headless=new")  
    # https://developer.mozilla.org/en-US/docs/Glossary/User_agent
    chrome_options.add_argument(f"--user-agent={user_agent}")  
    # https://stackoverflow.com/questions/53039551/selenium-webdriver-modifying-navigator-webdriver-flag-to-prevent-selenium-detec
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # Initialize the WebDriver
    webdriver_setup = Web_Driver_Setup(options = chrome_options)
    driver = webdriver_setup.initialize_driver()

    # Initialize the scraper
    scraper = Reddit_Scraper(driver = driver)

    data = scraper.scrape_subreddit("https://www.reddit.com/r/wallstreetbets/", 10)
    with open('scraped_data.json', 'w') as fp:
            json.dump(data, fp)

    # Quit the driver when done
    webdriver_setup.quit_driver()