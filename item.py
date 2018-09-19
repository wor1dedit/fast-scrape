import requests
from bs4 import BeautifulSoup


class Item:
    def __init__(self, id):
        self.id = id
        self.info = {"brand": None, "description": None, "msrp": None, "model": None, "load": None, "lotter": None, "width": None,
                     "depth": None, "height": None, "weight": None, "info": None, "location": None}

    def get_info(self, auction_id, location):
        page_item = requests.get("https://bid.bidfta.com/cgi-bin/mnlist.cgi?{}{}/{}".format(location, auction_id, self.id))
        soup_item = BeautifulSoup(page_item.content, 'html.parser')

        item = soup_item.find('tr', class_="DataRow")

        info = []

        b = item.find_all('b')
        for tb in b:
            if tb.string == "Front Page":
                break

            if len(tb.next_sibling[2:]) > 0:
                info.append((tb.string, tb.next_sibling.string[2:]))

        self.parse_info(info)

    def parse_info(self, info):
        for fo in info:
            title = fo[0].lower()
            if title == 'item brand':
                self.info['brand'] = fo[1]
            elif title == 'item desc':
                self.info['description'] = fo[1]
            elif title == 'msrp':
                self.info['msrp'] = fo[1]
            elif title == 'model':
                self.info['model'] = fo[1]
            elif title == 'load #':
                self.info['load'] = fo[1]
            elif title == 'lotter':
                self.info['lotter'] = fo[1]
            elif title == 'width':
                self.info['width'] = fo[1]
            elif title == 'depth':
                self.info['depth'] = fo[1]
            elif title == 'height':
                self.info['height'] = fo[1]
            elif title == 'weight':
                self.info['weight'] = fo[1]
            elif title == 'additional info':
                self.info['info'] = fo[1]
            elif title == 'item location':
                self.info['location'] = fo[1]
