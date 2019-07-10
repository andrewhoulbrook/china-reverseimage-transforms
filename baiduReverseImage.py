#!/usr/bin/python
# -*- encoding: utf-8 -*-
# Maltego local transform to retrieve results from a reverse image search via images.baidu.com (Baidu Images)
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

# Instantitate a Maltego transform object
m = MaltegoTransform()

# Parse arguements passed from Maltego entities with a field named 'url'
m.parseArguments(sys.argv)
IMAGE_URL = m.getVar('url').decode('utf8')

# Create baidu reverse image search URL string
IMAGE_URL = urllib.quote_plus(IMAGE_URL)
URL = "http://image.baidu.com/n/pc_search?queryImageUrl={}".format(IMAGE_URL)

# Set fake user-agent and header to mimic a user's browser
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['platform'] = "WINDOWS"
capabilities['version'] = "39.0.2171.95"
dcap = dict(capabilities)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)

# Instanitate a browser object using the Selenium and chosen webdriver, e.g. browser = webdriver.Chrome(CHROME_PATH)
browser = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=dcap)

# Perform reverse image search
try: 
    browser.get(URL)
    browser.set_page_load_timeout(60)

    # Wait for reverse image search results to load
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.imglist-content')))

except Exception as browser_err:
    m.addUIMessage(str(browser_err), 'FatalError')   

# Targets for scraping: baidu's image URL and the original source URL
img_urls = []
source_urls = []

# Scrape results from reverse image search
try:
    # Locate javacript containing list of source URLs for each reverse image search result
    head = browser.find_element(By.XPATH, '/html/head/script[4]')

    # If the script exists, scrape the source URLs that are embedded in script
    # The source URLs should be referenced in the same order as the list of images scrapped above
    if head: 
        soupHTML = head.get_attribute("innerHTML")
        soup = BeautifulSoup(soupHTML.encode('utf-8', errors='ignore'), 'html.parser')
        
        # Regex pattern matching for source URLs within the search results
        regex_source_urls = re.findall(r"\"fromURL\"\:\"(.*?)\"", soup.text)
        for regex_source_url in regex_source_urls: source_urls.append(regex_source_url.replace("\\", ""))

        # Regex pattern matching for the image URLs within the search results
        regex_img_urls = re.findall(r"\"objURL\"\:\"(.*?)\"", soup.text)
        for regex_img_url in regex_img_urls: img_urls.append(regex_img_url.replace("\\", ""))

    # Close the browser instance
    browser.quit()

    # Create Maltego entities for reverse image search results with additional fields of relevant meta-data
    if len(source_urls) > 0:
        for x in xrange(0, len(source_urls)):
            myEntity = m.addEntity('maltego.Website', source_urls[x].encode('utf8'))
            myEntity.addAdditionalFields('url', 'URL', False, source_urls[x].encode('utf8'))
            myEntity.addAdditionalFields('match-type', 'Match Type', False, "Baidu - Similar Match")
            myEntity.addAdditionalFields('search-engine', 'Search Engine', False, "Baidu Images")
            myEntity.setIconURL(img_urls[x].encode('utf8'))

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')

# Return Matlego entities to Maltego Chart
m.returnOutput()