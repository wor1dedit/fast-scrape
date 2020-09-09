import requests
from bs4 import BeautifulSoup
from fast_scrape.item import Item


class Auction:
    def __init__(self, auction, location="edwinmoses"):
        self.location = location
        self.auction_id = auction
        self.items = []

    def scrape_item_ids(self):
        page = requests.get("https://bid.bidfta.com/cgi-bin/mnlist.cgi?{}{}/category/ALL".format(self.location, self.auction_id))
        soup = BeautifulSoup(page.content, 'html.parser')

        # Search for item ids
        i = 1
        while True:
            item_list = soup.find('input', {"name":"p{}".format(i)})

            if item_list is None:
                break

            if "value" in item_list.attrs:
                item_list_split = item_list['value'].split("/")
                for item_id in item_list_split[:-1]:
                    self.items.append(Item(item_id))

            i += 1

    def scrape_item_info(self):
        for item in self.items:
            item.scrape_info(self.auction_id, self.location)
