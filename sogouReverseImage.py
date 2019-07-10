#!/usr/bin/python
# -*- encoding: utf-8 -*-
# Maltego local transform to retrieve results from a reverse image search via Sogou.com
import sys, codecs, re
import urllib
from MaltegoTransform import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from fake_useragent import UserAgent

# Set path to either chosen webdriver, e.g. CHROME_PATH = './chromedriver.exe'
PHANTOMJS_PATH = './phantomjs.exe'

# Instantitate a user-agent object
ua = UserAgent()

# Instantiate a Maltego transform
m = MaltegoTransform()

# Parse arguements passed from Maltego entities with a field named 'url'
m.parseArguments(sys.argv)
IMAGE_URL = m.getVar('url').decode('utf8')

# Create sogou reverse image search URL strings for exact matching and visually similar image results
IMAGE_URL = urllib.quote_plus(IMAGE_URL)
SIMILAR_URL = "https://pic.sogou.com/ris?flag=1&drag=0&query={}&flag=1&reqType=ajax&reqFrom=result".format(IMAGE_URL)
MATCHING_URL = "https://pic.sogou.com/ris/result?query={}&flag=0&scope=ss".format(IMAGE_URL)

# Set fake user-agent and header to mimic a user's browser
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['platform'] = "WINDOWS"
capabilities['version'] = "39.0.2171.95"
dcap = dict(capabilities)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)

# Instantiate a browser entity using Selenium and chosen webdriver, e.g. browser = webdriver.Chrome(CHROME_PATH)
browser = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=dcap)

# Perform reverse image search
try:
    browser.get(MATCHING_URL)
    browser.set_page_load_timeout(60)

    # Wait for reverse image search results to load
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.result-pannel')))

except Exception as browser_err:
    m.addUIMessage(str(browser_err), 'FatalError')

# Targets for scrapping: sogou's image URL and the orignal source URL
img_urls = []
source_urls = []

# Scrape data relating to exact matches found by reverse image search
try:
    # Select the reverse image search results
    imglist = browser.find_element(By.CSS_SELECTOR, 'div.result-pannel')

    # If matching images are found, scrape their sogou URLs
    if imglist:
        soupHTML = imglist.get_attribute("innerHTML")
        soup = BeautifulSoup(soupHTML.encode('utf-8', errors='ignore'), 'html.parser')
        imgdivs = soup.find_all('div', {'class', 'list-1-img'})
        if imgdivs:
            for imgdiv in imgdivs:
                imgrefs = soup.find_all('a', href=True)
                if imgrefs:
                    for imgref in imgrefs:
                        # Scrape out the source URL
                        source_urls.append(imgref['href'].encode('utf8'))

                        # Scrape out the Sogou image URL                    
                        imgurl = soup.find('img', src=True)
                        img_urls.append(imgurl['src'].encode('utf8'))                   

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')

# Targets for scrapping: sogou's image URL and the orignal source URL for visually similar images found
similar_img_urls = []
similar_source_urls = []

# Crawl additional link to find sogou's similar images search results
try:
    browser.get(SIMILAR_URL)
    WebDriverWait(browser, 5)

except Exception as browser_err:
    m.addUIMessage(str(browser_err), 'FatalError')

# SCrape data relating to exact matches. Regex pattern matching for source and image URLs contained within embedded JS array
try:
    # Regex pattern matching for image urls of visually similar images
    regex_img_urls = re.findall(r"\"pic_url\"\:\"(.*?)\"", browser.page_source)
    for regex_img_url in regex_img_urls: similar_img_urls.append(regex_img_url.replace("\\", ""))

    # Regex pattern matching for source urls of visually similar images
    regex_source_urls = re.findall(r"\"page_url\"\:\"(.*?)\"", browser.page_source)
    for regex_source_url in regex_source_urls: similar_source_urls.append(regex_source_url.replace("\\", ""))

    # Close the browser instance
    browser.quit()

    # Create Maltego entities for exact matches found by reverse image search
    for x in xrange(0, len(img_urls)):
        myExactEntity = m.addEntity('maltego.Website', source_urls[x])
        myExactEntity.addAdditionalFields('url', 'URL', False, source_urls[x])
        myExactEntity.addAdditionalFields('match-type', 'Match Type', False, "Exact Match")
        myExactEntity.addAdditionalFields('search-engine', 'Search Engine', False, "Sogou Images")
        myExactEntity.setBookmark(BOOKMARK_COLOR_RED)     # Add bookmark to entity to more easily distinguish and select exact matches from within the set of search results 
        myExactEntity.setLinkColor('#bd1717')             # Set entity link colour to RED to also help more easily distinguish exact matches in search results

    # Create Maltego entities for visually similar matches found by reverse image search
    for x in xrange(0, len(similar_img_urls)):
        mySimilarEntity = m.addEntity('maltego.Website', similar_source_urls[x])
        mySimilarEntity.addAdditionalFields('url', 'URL', False, similar_source_urls[x])
        mySimilarEntity.addAdditionalFields('match-type', 'Match Type', False, "Similar Match")
        mySimilarEntity.addAdditionalFields('search-engine', 'Search Engine', False, "Sogou Images")
        mySimilarEntity.setIconURL(similar_img_urls[x])

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')

# Return Matlego entities to Maltego Chart
m.returnOutput()