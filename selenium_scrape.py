import re
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.bidfta.com"
auction_id = 47327
url = "https://www.bidfta.com/auctionItems?idauctions={auction_id}&pageId={page_id}"

driver = webdriver.Firefox()
driver.implicitly_wait(3)

driver.get(url.format(auction_id=auction_id, page_id=1))
page_source_1 = driver.page_source
soup = BeautifulSoup(driver.page_source, 'html.parser')

items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView "})

more_items = True

while more_items:
    try:
        but = driver.find_element_by_xpath("//span[@class='next']")
        but.click()
    except NoSuchElementException:
        more_items = False
        break

    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    found_items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView "})

    items = [*items, *found_items]

for item in items:
    partial_url = item.contents[1].contents[1].contents[1].contents[1].attrs["href"]
    partial_url = partial_url[:partial_url.find("&firstIdItem")]
    print(partial_url)

driver.quit()

