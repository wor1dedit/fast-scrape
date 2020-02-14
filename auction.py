import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class Auction:
    def __init__(self, auction_id, base_url="https://www.bidfta.com", wait_time=4):
        self.base_url = base_url
        self.auction_url = "{base_url}/auctionItems?idauctions={auction_id}&pageId={page_id}"
        self.auction_id = auction_id
        self.wait_time = wait_time
        self.items = []

    def scrape_item_ids(self, use_next=True):
        # Starts up firefox
        driver = webdriver.Firefox()
        driver.implicitly_wait(self.wait_time)
        page_id = 1

        # Gets first page of the auction
        driver.get(self.auction_url.format(base_url=self.base_url, auction_id=self.auction_id, page_id=page_id))

        # Starts the BeautifulSoup Parser using the auction page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Finds items in html source
        items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView "})

        # Move onto the next page and search for items
        while True:
            if use_next:
                try:
                    # Finds the button to the next page
                    but = driver.find_element_by_xpath("//span[@class='next']")
                    but.click()
                except NoSuchElementException:
                    break
            else:
                page_id += 1
                driver.get(self.auction_url.format(base_url=self.base_url, auction_id=self.auction_id, page_id=page_id))

            # Lets the page load before scraping
            time.sleep(self.wait_time)

            # Starts the BeautifulSoup Parser using the current auction page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Finds items in html source and adds it to the found items
            found_items = soup.find_all("div", attrs={"class": "col-md-12 product-list listView "})

            for found_item in found_items:
                item_info = found_item.contents[1].contents[1].contents[1].contents[1].attrs["href"]
                try:
                    item_id = re.search(r"(?<=idItems=)\d+", item_info).group(0)
                    self.items.append(item_id)
                except IndexError:
                    continue

    def scrape_item_info(self):
        # WIP
        pass


if __name__ == "__main__":
    auction = Auction(47327)
    auction.scrape_item_ids()
