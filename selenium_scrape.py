from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

base_url = "https://www.bidfta.com"
auction_id = 47327
url = "https://www.bidfta.com/auctionItems?listView=true&idauctions={auction_id}&pageId={page_id}"

driver = webdriver.Firefox()
driver.implicitly_wait(3)

driver.get(url.format(auction_id=auction_id, page_id=1))
page_source_1 = driver.page_source
soup = BeautifulSoup(driver.page_source, 'html.parser')

items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView"})

more_items = True

while more_items:
    try:
        # Find next button and click it when possible
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='next']"))).click()
    except (NoSuchElementException, TimeoutException):
        more_items = False
        break

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all items on the page
    found_items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView"})

    items.extend(found_items)

for item in items:
    # Print out partial url of the item
    partial_url = item.contents[1].contents[1].contents[1].contents[1].attrs["href"]
    partial_url = partial_url[:partial_url.find("&firstIdItem")]
    print(partial_url)

driver.quit()

