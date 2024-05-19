# https://brightdata.com/blog/web-data/how-to-scrape-reddit-python

from selenium.webdriver.common.by import By
import time

class Reddit_Scraper:
    def __init__(self, driver):
        self.driver = driver

    def scrape_subreddit(self, subreddit_link, n_posts = 100):
        """
            inputs: 
                subreddit_link, a string that is a link to a specific subreddit
                n_posts, the number of posts to retrieve from the subreddit
        """
        # storage for all the data scraped 
        subreddit_data = {}

        # connect to the target URL in Selenium
        self.driver.get(subreddit_link)

        # scraping logic...
        name = self.driver.find_element(By.TAG_NAME, 'h1').text

        #right click on element 
        #select inspect 
        #go to line(s) highlighted in orange 
        #right click on orange then hover over "copy"
        #click on "copy JS path"
        #this is one way to do it 
        #you can also do it via find_element(s) and get attribute like way with posts
        #For shadowroots you need to use execute script!!!!
        description = self.driver.execute_script("""return document \
                                                            .querySelector("#subreddit-right-rail__partial > aside > div > shreddit-subreddit-header") \
                                                            .shadowRoot \
                                                            .querySelector("#description") \
                                                            .innerText""")

        members = self.driver.execute_script("""return document \
                                                            .querySelector("#subreddit-right-rail__partial > aside > div > shreddit-subreddit-header") \
                                                            .shadowRoot \
                                                            .querySelector("#subscribers > faceplate-number") \
                                                            .innerText""")

        subreddit_data['name'] = name
        subreddit_data['description'] = description
        subreddit_data['members'] = members


        #stores all posts scraped, will add to "subreddit_data" later 
        posts = []
        # this will store each of the post's html 
        # most of the posts have a tag "article" that is the root of the "html tree"
        # then it b
        post_html_elements = []

        # variable to keep track of the number of posts scraped 
        num_posts = 0
        # set the number of posts to scrape off the subreddit
        # or else for big subreddits the scraping will take forever 
        n_posts2scrape = 10
        while True:
            # this simulates the user scrolling down get load more posts
            # without this and only calling "driver.find_elements(By.CSS_SELECTOR, 'article.w-full.m-0')"
            # will only scrape 3 posts 
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for new posts to load
            time.sleep(10) 

            # get all posts 
            # if you Inspect each of the posts on a subreddit you will see that each of them has an "article"
            # tag with "w-full" and "m-0" classes, this line of code (find_elements) basically gets each of the posts 
            # by locating the html lines with an "article" tag then stores them in a list 
            new_posts = self.driver.find_elements(By.CSS_SELECTOR, 'article.w-full.m-0')

            #if the number of posts equals or exceeds the number of posts needed to be scraped 
            if len(new_posts) == num_posts or n_posts2scrape <= num_posts:
                break  # Break the loop if no new posts are loaded
            
            # update the number of total posts found after scrolling for 10 more seconds 
            # typically, based on the speed of your broser, it will get 20 - 50 posts each 10 secs 
            num_posts = len(new_posts)
            
            # updates the variable storing the htmls of posts to be scraped 
            post_html_elements = new_posts

        # itereate through the post htmls 
        for post_html_element in post_html_elements:
            # https://stackoverflow.com/questions/71885891/urllib3-exceptions-maxretryerror-httpconnectionpoolhost-localhost-port-5958
            # stores the data scraped from the current post 
            post = {}

            # get the title of the post 
            title = post_html_element.get_attribute('aria-label')
            post["title"] = title

            try:
                # hrefs exist mainly in subreddits like r/technology, where there are 
                # links to external articlecs within each of the posts
                # note that all posts will have title so it will not raise an exception
                elements_with_href = post_html_element \
                                .find_element(By.CSS_SELECTOR, "shreddit-post") \
                                .find_elements(By.CSS_SELECTOR, "[href]") 
                post["links"] = []
                for element in elements_with_href:
                    link = element.get_attribute("href")
                    post["links"].append(link)
            except:
                raise("links to article not found")

            try:
                # get timestamp of each post
                # note that all posts will have a timestamp so it will not raise an exception
                timestamp = post_html_element \
                                .find_element(By.TAG_NAME, "faceplate-timeago") \
                                .find_element(By.TAG_NAME, "time") \
                                .get_attribute("title")
                post["timestamp"] = timestamp
            except:
                raise("timestamp not found")

            try:
                # get body or written content/paragraph of each post
                # some posts will not have any content and just a link 
                # like the posts in r/technology so this exception will
                # be raised quite frequently 
                p_tags = post_html_element \
                                .find_element(By.TAG_NAME, "shreddit-post") \
                                .find_elements(By.TAG_NAME, "p") 
                body = " ".join([p.text for p in p_tags])
                post["body"] = body
            except:
                raise("body not found")

            try:
                #get the number of upvotes for current post 
                # note that all posts will have upvotes so it will not raise an exception
                upvotes = post_html_element \
                                .find_element(By.CSS_SELECTOR, "shreddit-post") \
                                .shadow_root \
                                .find_element(By.CLASS_NAME, 'pt-xs') \
                                .find_element(By.XPATH, 'div/span/span/span/faceplate-number').text
                post["upvotes"] = upvotes
            except:
                # for some reason the posts with videos have a different path to the upvotes 
                # this different path is hidden under a shadow DOM/root 
                # the only method I found that can access htmls 
                # embedded into a shadow dom is using javascript and "execute_script"
                upvotes = self.driver.execute_script("""return arguments[0] \
                                                                .querySelector("shreddit-post") \
                                                                .shadowRoot \
                                                                .querySelector("div > span > span > span > faceplate-number") \
                                                                .innerText""", post_html_element)
                post["upvotes"] = upvotes
        
            posts.append(post)

        subreddit_data['posts'] = posts

        return subreddit_data