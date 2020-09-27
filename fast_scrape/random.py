import urllib3

url = "https://www.bidfta.com/itemDetails?pageId=1&idauctions=71349&idItems=5957315&firstIdItem=5957315&source=auctionItems&lastIdItem=5957349"

http = urllib3.PoolManager()
x = http.request("POST", url)

print(x.text)
