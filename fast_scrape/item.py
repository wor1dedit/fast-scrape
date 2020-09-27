import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json


class Item:
    title_names = {
        "brand": "Brand name of item",
        "title": "Title of item",
        "msrp": "Maximum selling retail price of item",
        "model": "Item model number",
        "specs": "Item specification in detail",
        "width": "Item width dimension value",
        "depth": "Item depth dimension value",
        "length": "Item length dimension value",
        "weight": "Item width dimension value",
        "info": "Additional information of item condition",
        "location": "Pickup Location",
        "description": "Item description in details"
    }

    def __init__(self, url):
        self.url = f"https://www.bidfta.com{url}"
        self.info = {
            "brand": None,
            "description": None,
            "msrp": None,
            "model": None,
            "load": None,
            "lotter": None,
            "width": None,
            "depth": None,
            "height": None,
            "weight": None,
            "info": None,
            "location": None,
            "asin": None,
            "amazon msrp": None,
            "amazon cost": None,
        }

    def request_page_selenium(self, driver=None):
        """
        Scrape grab info from webpage

        :param driver: selenium web driver
        :return:
        """
        if driver is None:
            driver = webdriver.Firefox()
        driver.get(self.url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='bidHistoryIcon']")))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Check to see if read more button is present
        if soup.find("a", attrs={"class": "more"}):
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='more']"))).click()
            soup = BeautifulSoup(driver.page_source, "html.parser")

        self.parse_page(soup.find("div", attrs={"class": "p-description m-t-10"}))

    def parse_page(self, description):
        """
        Parse info of description for useful info about item

        :param description: Description part of auction item page
        """
        for k, v in self.title_names.items():
            try:
                self.info[k] = description.find("strong", attrs={"title": v}).next_sibling.strip()
            except AttributeError:
                try:
                    # Handle case when title is blank and data-original-title is used
                    self.info[k] = description.find("strong", attrs={"data-original-title": v}).next_sibling.strip()
                except AttributeError:
                    continue

            self.info["description"] = (
                description.find("strong", attrs={"data-original-title": "Item description in details"})
                .next_sibling.next_sibling.text.strip("  Read Less")
                .replace("... Read More", "", 1)
            )

    def scrape_amazon_info(self):
        if self.info["model"]:
            if self.info["brand"]:
                product_name = self.info["model"] + "+" + self.info["brand"]
            else:
                product_name = self.info["model"]
        else:
            print("No model number for item")
            return None

        # Convert spaces to pluses
        query_product_name = product_name.replace(" ", "+")

        # Query the title on Amazon.com
        asin_query_url = (
            "http://www.amazon.com/s/?url=search-alias%3Daps&field-keywords="
            + query_product_name
            + "&rh=i%3Aaps%2Ck%3A"
            + query_product_name
        )

        url_query = requests.get(asin_query_url)
        if url_query.status_code != 200:
            print("URL could not be opened")
            return None

        url_query_response = url_query.content

        soup = BeautifulSoup(url_query_response, "html.parser")

        # Finds first result
        query_result = soup.find(id="result_0")

        if query_result:
            dollar_amount = None
            cent_amount = None

            info = {"asin": None, "msrp": None, "price": None}

            # Get ASIN
            try:
                asin_string = query_result.attrs["data-asin"]
            except KeyError:
                print("Can't find ASIN")
                return None

            if asin_string:
                self.info["asin"] = asin_string

            # Get msrp
            msrp_query = query_result.find("span", class_="a-size-base-plus a-color-secondary a-text-strike")
            if msrp_query:
                split_msrp = re.findall(r"\d+", msrp_query.getText())
                if len(split_msrp) != 2:
                    print("Can't parse msrp")
                else:
                    try:
                        self.info["amazon msrp"] = tuple(int(part) for part in split_msrp)
                    except ValueError:
                        print("Error converting list of strings to tuple of ints in parse msrp")

            # Get current dollar amount
            dollar_query = query_result.find("span", class_="sx-price-whole")
            if dollar_query:
                try:
                    dollar_amount = int(dollar_query.getText())
                except ValueError:
                    print("Can't convert current dollar amount to int")

            # Get current cent amount
            cent_query = query_result.find("sup", class_="sx-price-fractional")
            if cent_query:
                try:
                    cent_amount = int(cent_query.getText())
                except ValueError:
                    print("Can't convert current cent amount to int")

            # Adds dollar and cents to info
            if dollar_amount:
                if cent_amount:
                    self.info["amazon price"] = (dollar_amount, cent_amount)
                else:
                    self.info["amazon price"] = (dollar_amount + 1, 0)

        return True

    def __str__(self):
        return str(json.dumps(self.info, indent=4))


if __name__ == "__main__":
    it = Item("/itemDetails?listView=true&pageId=4&idauctions=47327&idItems=3954584")
    it.request_page_selenium()
    it.scrape_amazon_info()
    print(it)
