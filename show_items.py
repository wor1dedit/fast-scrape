import auction

auction1154 = auction.Auction("iii1154")
auction1154.scrape_item_ids()
auction1154.scrape_item_info()
print(auction1154.items[0].info)
