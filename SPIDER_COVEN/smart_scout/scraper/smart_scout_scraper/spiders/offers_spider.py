import scrapy
from smart_scout_scraper.items import PriceItem
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup

def extract_coupon_value(html: str) -> float:
    """Detect checkbox coupon and return its INR value."""
    soup = BeautifulSoup(html, "lxml")

    # Pattern 1: "Coupon: Save ₹50"
    coupon_label = soup.find("label", {"class": re.compile(r"coupon|s-coupon", re.I)})
    if coupon_label:
        match = re.search(r"₹([\d,]+)", coupon_label.text)
        if match:
            return float(match.group(1).replace(",", ""))

    # Pattern 2: "5% off coupon" — convert percent to INR using base price
    pct_match = re.search(r"(\d+)%\s*off\s*(coupon|with coupon)", html, re.I)
    if pct_match:
        return None   # return None to signal "percent coupon — needs base price"

    return 0.0

class OffersSpider(scrapy.Spider):
    name = "offers_spider"

    def __init__(self, asin=None, pin_code="600001", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asin = asin
        self.pin_code = pin_code

    def start_requests(self):
        url = f"https://www.amazon.in/gp/offer-listing/{self.asin}?startIndex=0"
        yield scrapy.Request(url, callback=self.parse,
                             meta={
                                 "playwright": True,
                                 "playwright_include_page": True,
                                 "pin_code": self.pin_code,
                                 "start_index": 0
                             })

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
            is_fba = "Fulfilled by Amazon" in offer.get()
            is_bb = (i == 0)   # first offer is Buy Box winner

            coupon = extract_coupon_value(offer.get()) or 0.0
            net_price = (price + ship) - coupon

            stock_left = None
            stock_match = re.search(r"only\s+(\d+)\s+left\s+in\s+stock", offer.get(), re.I)
            if stock_match:
                stock_left = int(stock_match.group(1))

            yield PriceItem(
                asin=self.asin, seller=seller,
                price=price, shipping=ship, total_price=price+ship,
                net_price=net_price, coupon_value=coupon,
                is_buy_box=is_bb, is_fba=is_fba, is_suspicious=False,
                pin_code=response.meta["pin_code"],
                dominance_score=net_price - (50 if is_fba else 0),
                stock_left=stock_left,
                scraped_at=datetime.now(timezone.utc).isoformat()
            )

        # Paginate
        next_index = response.meta["start_index"] + 10
        if len(offers) == 10:
            next_url = f"https://www.amazon.in/gp/offer-listing/{self.asin}?startIndex={next_index}"
            yield scrapy.Request(next_url, callback=self.parse,
                                 meta={"pin_code": self.pin_code, "start_index": next_index})
