#https://brightdata.com/blog/web-data/how-to-scrape-reddit-python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import sys
import time

#for the future when we have rotating proxies 
#we will continuously rotate the user_agent
#https://stackoverflow.com/questions/56889999/how-to-rotate-proxies-and-user-agents

#to get your own local user agent 
#literally jst search up "how to get user agent from browser"
#in google and the first thing that will pop up is a section "Your user agent"
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

# enable the headless mode
options = Options()
#this doesn't work figure out why 
options.add_argument('--headless=new')
options.add_argument(f"user-agent={user_agent}")
options.add_argument('--disable-blink-features=AutomationControlled')

# initialize a web driver to control Chrome
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)
driver.delete_all_cookies()
# maxime the controlled browser window
driver.fullscreen_window()

# the URL of the target page to scrape
#if you replace 'www' with 'new' there will not be any more shadow doms 
#you can use "xpath" instead of "JS path" + execute_script after the change
#never got xpath to work tho :/
#driver.get_element(By.XPATH, "")
#might be worth looking into but I don't fully understnat how XPATH works
url = 'https://www.reddit.com/r/wallstreetbets/'

#
# connect to the target URL in Selenium
driver.get(url)

# scraping logic...
#------------------
#dictionary to store scraped data
subreddit = {}
name = driver \
    .find_element(By.TAG_NAME, 'h1') \
    .text

#right click on element 
#select inspect 
#go to line(s) highlighted in orange 
#right click on orange then hover over "copy"
#click on "copy JS path"
#this is one way to do it 
#you can also do it via find_element(s) and get attribute like way with posts
#For shadowroots you need to use execute script!!!!
description = driver.execute_script("""return document \
                                                    .querySelector("#subreddit-right-rail__partial > aside > div > shreddit-subreddit-header") \
                                                    .shadowRoot \
                                                    .querySelector("#description") \
                                                    .innerText""")

members = driver.execute_script("""return document \
                                                    .querySelector("#subreddit-right-rail__partial > aside > div > shreddit-subreddit-header") \
                                                    .shadowRoot \
                                                    .querySelector("#subscribers > faceplate-number") \
                                                    .innerText""")

subreddit['name'] = name
subreddit['description'] = description
subreddit['members'] = members


#scrape posts
#post_html_elements = driver.find_elements(By.CSS_SELECTOR, 'article.w-full.m-0')

#stores all posts scraped 
posts = []
#
post_html_elements = []
num_posts = 0
n_posts2scrape = 10

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)  # Wait for new posts to load
    new_posts = driver.find_elements(By.CSS_SELECTOR, 'article.w-full.m-0')
    if len(new_posts) == num_posts or n_posts2scrape < num_posts:
        break  # Break the loop if no new posts are loaded
    num_posts = len(new_posts)
    post_html_elements = new_posts

for post_html_element in post_html_elements:
    #https://stackoverflow.com/questions/71885891/urllib3-exceptions-maxretryerror-httpconnectionpoolhost-localhost-port-5958
    # try:
    post = {}

    title = post_html_element.get_attribute('aria-label')
    post["title"] = title
    print(title)

    try:
        #hrefs exist mainly in subreddits like r/technology, where there are 
        #links to external articlecs within each of the posts 
        elements_with_href = post_html_element \
                        .find_element(By.CSS_SELECTOR, "shreddit-post") \
                        .find_elements(By.CSS_SELECTOR, "[href]") 
        post["links"] = set()
        for element in elements_with_href:
            link = element.get_attribute("href")
            post["links"].add(link)
        print(post["links"])
    except:
        print("links to articles not found")

    try:
        #get timestamp of each post
        timestamp = post_html_element \
                        .find_element(By.TAG_NAME, "faceplate-timeago") \
                        .find_element(By.TAG_NAME, "time") \
                        .get_attribute("title")
        post["timestamp"] = timestamp
        print(timestamp)
    except:
        print("timestamp not found")

    try:
        #get body or written content/paragraph of each post
        p_tags = post_html_element \
                        .find_element(By.TAG_NAME, "shreddit-post") \
                        .find_elements(By.TAG_NAME, "p") 
        body = " ".join([p.text for p in p_tags])
        post["body"] = body
        print(body)
    except:
        print("body not found")

    try:
        #get the number of upvotes for current post 
        upvotes = post_html_element \
                        .find_element(By.CSS_SELECTOR, "shreddit-post") \
                        .shadow_root \
                        .find_element(By.CLASS_NAME, 'pt-xs') \
                        .find_element(By.XPATH, 'div/span/span/span/faceplate-number').text
        post["upvotes"] = upvotes
        print(upvotes)
    except:
        #for some reason the posts with videos have a different path to the upvotes 
        upvotes = driver.execute_script("""return arguments[0] \
                                                        .querySelector("shreddit-post") \
                                                        .shadowRoot \
                                                        .querySelector("div > span > span > span > faceplate-number") \
                                                        .innerText""", post_html_element)
        post["upvotes"] = upvotes
        print(upvotes)
 
    posts.append(post)
    print()

    # except:
    #     driver.quit()
    #     print("\nScrapper stopped, launching again in 4 seconds...")
    #     time.sleep(4)
    #     driver = webdriver.Chrome(
    #         service=ChromeService(ChromeDriverManager().install()),
    #         options=options
    #     )
    #     driver.delete_all_cookies()
    #     driver.get(url)

subreddit['posts'] = posts

with open('scraped_data.json', 'w') as fp:
    json.dump(subreddit, fp)