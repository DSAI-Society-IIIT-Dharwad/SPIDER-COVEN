# Smart Scout — Real-time Amazon.in Price Monitor

## Project Overview
Smart Scout empowers Amazon.in bearing distributors (SKF) to monitor competitor prices in real-time across multiple locations. By aggregating prices, logisitics information, and buy-box winners using local pin codes, it computes dominance scores and alerts sellers when they are being undercut. All of this runs natively on localhost without requiring Docker infrastructures.

## Quickstart (5 commands)

```bash
git clone <repo> && cd smart_scout
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill SCRAPEOPS_API_KEY and YOUR_SELLER_NAME
python run.py          # starts everything — open localhost:8501
```

## Environment variables
```env
DATABASE_URL=sqlite:///./scout.db
REDIS_URL=none
SCRAPEOPS_API_KEY=get-free-key-at-scrapeops.io
YOUR_SELLER_NAME=YourExactSellerNameOnAmazon
TRACKED_ASINS=B07SKKG51W,B07PQKK9FB
PIN_CODES=600001,110001,500001,400001
```

> **Note on Deduplication**: Redis usage is disabled by default for the demo since it runs via APScheduler on Windows natively and deduplicates via Scout SQLite directly.

## Stealth Layer
Amazon employs heavy anti-scraping measures. To bypass these, we use a multi-layered stealth approach:
1. **Proxy Rotation**: ScrapeOps handles IP rotation per request internally across the Indian region.
2. **TLS Fingerprinting Evasion**: The `curl_cffi` module replaces Scrapy's primitive TLS handshake with an imitation of a Chrome 120 browser.
3. **Pincode Cookie Injections**: The `LocationMiddleware` explicitly passes precise `delivery-zip-code` cookies mapped to local Indian cities.
4. **Heuristic Parsing Models**: Prices are extracted probabilistically by analyzing their DOM distance to static elements like the Add-to-Cart button, ignoring ephemeral CSS classes.
5. **Javascript Failover**: JS-heavy pages failing basic extraction seamlessly default to `playwright-chromium` to load the dynamic DOM naturally.

## Running spiders manually
To execute scraping commands independently, open your activated virtual environment terminal:
```bash
scrapy crawl search_spider -a query="SKF 6205"
scrapy crawl offers_spider -a asin=B07SKKG51W -a pin_code=600001
scrapy crawl product_spider -a asin=B07SKKG51W
```

## Known Limitations
- Not all product discount structures are parsable; percentage coupons require cross-calculating from the MSRP base price which is often obfuscated.
- Amazon iterates heavily on their product detail UI; element ids sometimes shift between sub-types of items (e.g., FBA vs Merchant Fulfillment layout differences), triggering the JS-playwright failover more often.
