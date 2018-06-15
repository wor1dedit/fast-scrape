from bs4 import BeautifulSoup
import requests

resp = requests.get("https://bid.bidfta.com/cgi-bin/mndetails.cgi?edwinmosesiii1437")
soup = BeautifulSoup(resp.content, "html.parser")
para = soup.find_all('p')
strongs = soup.find_all('strong')
i = -1
for par in para:
    i += 1
    if par.get_text().find("REMOVAL") == 0:
        print("re")
        print(i)
        print(par)
i = -1
for strong in strongs:
    i += 1
    if strong.get_text().find("Date & Time") == 0:
        print("dt")
        print(i)
        print(strong)
        strong_parent = strong.find_parent()
        print(strong_parent)
        print(strong_parent.find_sibling)
