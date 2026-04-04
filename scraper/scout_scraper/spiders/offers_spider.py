import scrapy
from scout_scraper.items import PriceItem
from datetime import datetime, timezone

class OffersSpider(scrapy.Spider):
    name = "offers_spider"

    def __init__(self, asin=None, pin_code="600001", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asin = asin
        self.pin_code = pin_code

    def start_requests(self):
        url = f"https://www.amazon.in/gp/offer-listing/{self.asin}?startIndex=0"
        yield scrapy.Request(url, callback=self.parse,
                             meta={"pin_code": self.pin_code, "start_index": 0})

    def parse(self, response):
        offers = response.css(".a-row.olpOffer")
        for i, offer in enumerate(offers):
            seller = offer.css(".olpSellerName span::text").get("").strip()
            if not seller:
                seller = offer.css(".olpSellerName a::text").get("").strip()
            price_text = offer.css(".olpOfferPrice::text").get("")
            ship_text = offer.css(".olpShippingInfo .olpShippingPrice::text").get("0")
            price = float(price_text.replace("₹","").replace(",","").strip() or 0)
            ship = float(ship_text.replace("₹","").replace(",","").strip() or 0)
            is_fba = "Fulfilled by Amazon" in offer.text
            is_bb = (i == 0)   # first offer is Buy Box winner

            yield PriceItem(
                asin=self.asin, seller=seller,
                price=price, shipping=ship, total_price=price+ship,
                net_price=price+ship, coupon_value=0,
                is_buy_box=is_bb, is_fba=is_fba, is_suspicious=False,
                pin_code=response.meta["pin_code"],
                dominance_score=(price+ship) - (50 if is_fba else 0),
                scraped_at=datetime.now(timezone.utc).isoformat()
            )

        # Paginate
        next_index = response.meta["start_index"] + 10
        if len(offers) == 10:
            next_url = f"https://www.amazon.in/gp/offer-listing/{self.asin}?startIndex={next_index}"
            yield scrapy.Request(next_url, callback=self.parse,
                                 meta={"pin_code": self.pin_code, "start_index": next_index})