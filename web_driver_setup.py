# https://www.selenium.dev/selenium/docs/api/py/webdriver_chrome/selenium.webdriver.chrome.webdriver.html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class Web_Driver_Setup:
    def __init__(self, options = None):
        self.options = options if options else webdriver.ChromeOptions()
        self.driver = None

    def initialize_driver(self):
        """
            Initializes the Chrome WebDriver with the specified options.
        """
        self.driver = webdriver.Chrome(
            service = ChromeService(ChromeDriverManager().install()),
            options = self.options
        )
        return self.driver

    def delete_cookies(self):
        """
            clears all cookies associated with the driver 
        """
        # deleting the cookies make you seem like a new user, use this  
        # periodically to make sure that the website doesn't think you're a bot 
        self.driver.delete_all_cookies()

    def quit_driver(self):
        """
            Quits the WebDriver.
        """
        # use this after you are done scraping 
        if self.driver:
            self.driver.quit()