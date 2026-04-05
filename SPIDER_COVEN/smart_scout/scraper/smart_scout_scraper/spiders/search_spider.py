import scrapy
from smart_scout_scraper.items import PriceItem
from datetime import datetime, timezone

class SearchSpider(scrapy.Spider):
    name = "search_spider"
    custom_settings = {"FEEDS": {}}

    def __init__(self, query="SKF bearing 6205", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = query.replace(" ", "+")

    def start_requests(self):
        for page in range(1, 6):   # start with 5 pages
            url = f"https://www.amazon.in/s?k={self.query}&page={page}"
            yield scrapy.Request(url, callback=self.parse,
                                 meta={"playwright": False})

    def parse(self, response):
        for card in response.css("[data-component-type=s-search-result]"):
            asin = card.attrib.get("data-asin", "").strip()
            if not asin:
                continue
            if card.css("[data-component-type=sp-sponsored-result]"):
                continue
            title = card.css("h2 span::text").get(default="").strip()
            self.logger.info(f"Found ASIN: {asin} — {title}")
            yield PriceItem(
                asin=asin, title=title,
                scraped_at=datetime.now(timezone.utc).isoformat()
            )
