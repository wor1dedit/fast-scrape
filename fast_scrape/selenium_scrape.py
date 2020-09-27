import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup

from fast_scrape.item import Item

logging.basicConfig(filename="../selenium_scrape.log", filemode="w", format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logging.warning('This is a Warning')

base_url = "https://www.bidfta.com"
auction_id = 47327
url = "https://www.bidfta.com/auctionItems?listView=true&idauctions={auction_id}&pageId={page_id}"

driver = webdriver.Firefox()
driver.implicitly_wait(5)

driver.get(url.format(auction_id=auction_id, page_id=1))
soup = BeautifulSoup(driver.page_source, 'html.parser')

items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView"})

more_items = True

while more_items:
    try:
        # Find next button and click it when possible
        logging.info("Scraping next page")
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='next']"))).click()
    except (NoSuchElementException, TimeoutException):
        more_items = False
        break
    except (ElementClickInterceptedException, StaleElementReferenceException):
        logging.info("Issue with element click: Trying execute script method")
        element = driver.find_element_by_xpath("//span[@class='next']")
        driver.execute_script("arguments[0].click();", element)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Find all items on the page
    found_items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView "})

    items.extend(found_items)

auction_items = []

for item in items:
    # Print out partial url of the item
    partial_url = item.contents[1].contents[1].contents[1].contents[1].attrs["href"]
    partial_url = partial_url[:partial_url.find("&firstIdItem")]
    it = Item(partial_url)
    it.request_page_selenium(driver)
    auction_items.append(it)

for item in auction_items:
    print(item)

driver.quit()
