#!/usr/bin/python
# -*- encoding: utf-8 -*-
# Maltego local transform to retrieve results from a reverse image search via 360 (so.com)
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
import requests

# Set path to your chosen webdriver, e.g. CHROME_PATH = './chromedriver.exe'
PHANTOMJS_PATH = './phantomjs.exe'

# Instantitate a user-agent object
ua = UserAgent()

# Instantiate a Maltego transform object
m = MaltegoTransform()

# Parse arguements passed from Maltego entities with a field named 'url'
m.parseArguments(sys.argv)
IMAGE_URL = m.getVar('url').decode('utf8')

MATCHING_URL = None
SIMILAR_URL = None
API_ENDPOINT = 'http://st.so.com/stu'

# POST request payload
data = {'imgurl': IMAGE_URL,
        'submittype': 'imgurl',
        'src': 'image',
        'srcsp': 'st_search'} 

# Call the images.so.com reverse search API, returns html 
try:
    page_html = requests.post(url=API_ENDPOINT, data=data) 

except Exception as call_err:
    m.addUIMessage(str(call_err), 'FatalError')  

# Targets for scrapping: 360's image URL and the orignal source URL
img_urls = []
source_urls = []

# Get the 'imgkey' variable in order to construct new URLs. Extract imgkey using a Regex pattern
try:
    regex_imgkey = re.findall(r"data-imgkey=\"(.*?)\"", page_html.text)
    MATCHING_URL = "http://st.so.com/stu?a=siftwaterfall&imgkey={}&cut=0".format(regex_imgkey[0])
    SIMILAR_URL = "http://st.so.com/stu?a=list&imgkey={}&tp=imgurl&src=image&keyword=&guess=&sim=0&camtype=1&srcsp=st_search".format(regex_imgkey[0])

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')  

# Get results for exact image matches 
try:
    matches_html = requests.get(MATCHING_URL)

except Exception as call_err:
    m.addUIMessage(str(call_err), 'FatalError')  

# Scrape data relating to exact matches found by reverse image search
try:
    # Regex pattern matching for image urls of exact matching images
    regex_img_urls = re.findall(r"\"thumb\"\:\"(.*?)\"", matches_html.text)
    for regex_img_url in regex_img_urls: img_urls.append(regex_img_url.replace("\\", ""))

    # Regex pattern matching for source urls of exact matching images
    regex_source_urls = re.findall(r"\"link\"\:\"(.*?)\"", matches_html.text)
    for regex_source_url in regex_source_urls: source_urls.append(regex_source_url.replace("\\", ""))

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')  

# Targets for scrapping: 360's image URL and the orignal source URL for visually similar images
similar_img_urls = []
similar_source_urls = []

# Set fake user-agent and header to mimic a user's browser
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['platform'] = "WINDOWS"
capabilities['version'] = "39.0.2171.95"
dcap = dict(capabilities)
dcap["phantomjs.page.settings.userAgent"] = (ua.random)

# Instantiate a browser entity using Selenium and chosen webdriver, e.g. browser = webdriver.Chrome(CHROME_PATH)
browser = webdriver.PhantomJS(PHANTOMJS_PATH, desired_capabilities=dcap)

# Perform reverse image search for visually similar images
try:
    browser.get(SIMILAR_URL)
    browser.set_page_load_timeout(60)

    # Wait for reverse image search results to load
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#bd')))

except Exception as browser_err:
    m.addUIMessage(str(browser_err), 'FatalError')  

# Scrape data related to visually similar matches found by reverse image search
try:
    # Select the 'visually similar' list of image results  
    imglist = browser.find_element(By.CSS_SELECTOR, 'div.like-content')

    # Scrape out details from DOM of visually similar image matches found
    if imglist:
        soupHTML = imglist.get_attribute("innerHTML")
        soup = BeautifulSoup(soupHTML.encode('utf-8', errors='ignore'), 'html.parser')
        rows = soup.find_all('ul', {'class', 'wfx_row'})
        if rows:
            for row in rows: 
                matches = row.find_all('li')
                if matches:
                    for match in matches: 
                        imgurl = match.find('a', href=True)

                        # Regex to patten match the original source URL embbedded within a larger URL string
                        regex_source_url = re.findall(r"fromurl=(.*)", imgurl['href'].encode('utf8'))
                        similar_source_urls.append(regex_source_url[0]) 

                        # Scrape out 360 image URL 
                        imgsrc = match.find('img', src=True)
                        similar_img_urls.append(imgsrc['src'].encode('utf8'))

    # Close the browser instance
    browser.quit()

    # Create Maltego entities for exact matches found by reverse image search
    for x in xrange(0, len(img_urls)):
        myExactEntity = m.addEntity('maltego.Website', source_urls[x])
        myExactEntity.addAdditionalFields('url', 'URL', False, source_urls[x])
        myExactEntity.addAdditionalFields('match-type', 'Match Type', False, "Exact Match")
        myExactEntity.addAdditionalFields('search-engine', 'Search Engine', False, "Qihoo 360 Images")
        myExactEntity.setIconURL(img_urls[x])
        myExactEntity.setBookmark(BOOKMARK_COLOR_RED)      # Add bookmark to entity to more easily distinguish and select exact matches from within the set of search results 
        myExactEntity.setLinkColor('#bd1717')              # Set entity link colour to RED to also help more easily distinguish exact matches in search results

    # Create Maltego entities for visually similar matches found by reverse image search
    for x in xrange(0, len(similar_img_urls)):
        mySimilarEntity = m.addEntity('maltego.Website', similar_source_urls[x])
        mySimilarEntity.addAdditionalFields('url', 'URL', False, similar_source_urls[x])
        mySimilarEntity.addAdditionalFields('match-type', 'Match Type', False, "Qihoo 360 - Similar Match")
        mySimilarEntity.addAdditionalFields('search-engine', 'Search Engine', False, "Qihoo 360 Images")
        mySimilarEntity.setIconURL(similar_img_urls[x])

except Exception as scrape_err:
    m.addUIMessage(str(scrape_err), 'PartialError')

# Return Matlego entities to Maltego Chart
m.returnOutput()