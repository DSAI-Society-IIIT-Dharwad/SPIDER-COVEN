import scrapy
import re
from bs4 import BeautifulSoup
from scout_scraper.items import PriceItem
from datetime import datetime, timezone

def heuristic_price_extract(html: str) -> float:
    """Extracts price by proximity to Add-to-Cart button."""
    soup = BeautifulSoup(html, "lxml")
    atc = soup.find(id="add-to-cart-button")
    if not atc:
        atc = soup.find("input", {"value": re.compile(r"Add to Cart", re.I)})

    if atc:
        parent = atc.find_parent("form") or atc.find_parent("div")
        if parent:
            price_text = parent.find(text=re.compile(r"₹[\d,]+"))
            if price_text:
                match = re.search(r"₹([\d,]+)", price_text)
                if match:
                    return float(match.group(1).replace(",", ""))

    buybox = soup.find(id="buybox") or soup.find(id="desktop_buyBox")
    if buybox:
        price_text = buybox.find(text=re.compile(r"₹[\d,]+"))
        if price_text:
            match = re.search(r"₹([\d,]+)", price_text)
            if match:
                return float(match.group(1).replace(",", ""))

    return 0.0

def extract_coupon_value(html: str) -> float:
    """Detect checkbox coupon and return its INR value."""
    soup = BeautifulSoup(html, "lxml")
    coupon_label = soup.find("label", {"class": re.compile(r"coupon|s-coupon", re.I)})
    if coupon_label:
        match = re.search(r"₹([\d,]+)", coupon_label.text)
        if match:
            return float(match.group(1).replace(",", ""))
    # Percentage off
    pct_match = re.search(r"(\d+)%\s*off\s*(coupon|with coupon)", html, re.I)
    if pct_match:
        return None
    return 0.0

class ProductDetailSpider(scrapy.Spider):
    name = "product_spider"

    def __init__(self, asin=None, pin_code="600001", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asin = asin
        self.pin_code = pin_code

    def start_requests(self):
        url = f"https://www.amazon.in/dp/{self.asin}"
        yield scrapy.Request(url, callback=self.parse,
                             meta={"pin_code": self.pin_code})

    def parse(self, response):
        seller = response.css("#merchant-info a::text").get()
        if not seller:
            seller = response.css("#sellerProfileTriggerId::text").get()

        price_str = (
            response.css(".a-price.priceToPay .a-offscreen::text").get() or
            response.css("#priceblock_ourprice::text").get() or
            response.css(".a-price-whole::text").get("")
        )
        price = float(price_str.replace("₹","").replace(",","").strip() or 0)
        if price == 0:
            price = heuristic_price_extract(response.text)

        is_fba = "Amazon" in response.css("#merchant-info::text").get("") or \
                 "Fulfilled by Amazon" in response.text

        if "See all buying options" in response.text and not seller:
            offers_url = f"https://www.amazon.in/gp/offer-listing/{self.asin}"
            yield scrapy.Request(offers_url, callback=self.parse_offers,
                                 meta={"pin_code": self.pin_code})
            return

        if seller and price:
            coupon = extract_coupon_value(response.text) or 0.0
            net_price = price - coupon

            yield PriceItem(
                asin=self.asin, seller=seller.strip(),
                price=price, shipping=0, total_price=price,
                net_price=net_price, coupon_value=coupon,
                is_buy_box=True, is_fba=is_fba,
                is_suspicious=False,
                pin_code=response.meta["pin_code"],
                dominance_score=price - (50 if is_fba else 0),
                scraped_at=datetime.now(timezone.utc).isoformat()
            )

    def parse_offers(self, response):
        pass