import requests
from bs4 import BeautifulSoup


class Item:
    def __init__(self, id):
        self.id = id
        self.info = {"brand": None, "description": None, "msrp": None, "model": None, "load": None, "lotter": None,
                     "width": None, "depth": None, "height": None, "weight": None, "info": None, "location": None,
                     "asin": None, "amazon msrp": None, "amazon cost": None}

    def scrape_info(self, auction_id, location):
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
        query_product_name = product_name.replace(' ', '+')

        # Query the movie title on Amazon.com
        asin_query_url = "http://www.amazon.com/s/?url=search-alias%3Daps&field-keywords=" + query_product_name + "&rh=i%3Aaps%2Ck%3A" + query_product_name

        if sys.version_info > (3, 0):
            # Python 3
            url_query = requests.get(asin_query_url)
            if url_query.status_code != 200:
                print("URL could not be opened")
                return None
            url_query_response = url_query.content
        else:
            # Python 2
            try:
                url_query_response = urllib2.urlopen(asin_query_url)
            except urllib2.HTTPError:
                print("URL could not be opened")
                return None

        soup = BeautifulSoup(url_query_response, "html.parser")

        # Finds first result
        query_result = soup.find(id="result_0")

        if query_result:
            msrp = None
            dollar_amount = None
            cent_amount = None

            info = {"asin": None, "msrp": None, "price": None}

            # Get ASIN
            try:
                asin_string = query_result.attrs['data-asin']
            except Exception as e:
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
                    except Exception as e:
                        print("Error converting list of strings to tuple of ints in parse msrp")

            # Get current dollar amount
            dollar_query = query_result.find("span", class_="sx-price-whole")
            if dollar_query:
                try:
                    dollar_amount = int(dollar_query.getText())
                except Exception as e:
                    print("Can't convert current dollar amount to int")

            # Get current cent amount
            cent_query = query_result.find("sup", class_="sx-price-fractional")
            if cent_query:
                try:
                    cent_amount = int(cent_query.getText())
                except Exception as e:
                    print("Can't convert current cent amount to int")

            # Adds dollar and cents to info
            if dollar_amount:
                if cent_amount:
                    self.info["amazon price"] = (dollar_amount, cent_amount)
                else:
                    self.info["amazon price"] = (dollar_amount + 1, 0)

        return True
