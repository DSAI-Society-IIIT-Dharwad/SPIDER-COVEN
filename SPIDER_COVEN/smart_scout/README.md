# Smart Scout Price Monitor

Smart Scout is a robust, local-first proxy and data-analytics platform targeted specifically for bearing distributors actively combatting Buy Box price wars. It operates completely out-of-the-box leveraging dynamic stealth arrays locally avoiding external databases.

## Quickstart (5 commands)

```bash
git clone <repo> && cd smart_scout
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill SCRAPEOPS_API_KEY and YOUR_SELLER_NAME
python run.py          # starts everything — open localhost:8501
```

## Environment variables
The `.env` file structure is natively wired up using standard configurations natively checking internal variables bypassing `docker`.

```env
DATABASE_URL=sqlite:///./scout.db
REDIS_URL=redis://localhost:6379
SCRAPEOPS_API_KEY=get-free-key-at-scrapeops.io
YOUR_SELLER_NAME=YourExactSellerNameOnAmazon
TRACKED_ASINS=B07SKKG51W,B07PQKK9FB
PIN_CODES=600001,110001,500001,400001
```

## Anti-bot Stealth Layer Explained 
- **Geo Cookie Override:** Automatically manipulates Location zip variables actively simulating diverse IP searches per crawler iteration using `/delivery-zip-code`.
- **TLS Fingerprinting:** Uses active `curl_cffi` overrides injecting valid `JA3` browser signatures bypassing generalized Scrapy packet sniffing blocks.
- **Proxy Node Networks:** Disguises the local host natively using residential IP rotations avoiding local host blockage.
- **Heuristic Price Extractions:** We circumvent strict tag parsing failures leveraging raw BS4 scraping natively hunting DOM tree patterns.

## Manual spider commands
```bash
scrapy crawl search_spider -a query="SKF 6205"
scrapy crawl offers_spider -a asin=B07SKKG51W -a pin_code=600001
scrapy crawl product_spider -a asin=B07SKKG51W
```

## Known Limitations
*   Amazon has massive teams dedicated to stopping bot extraction. They regularly change their `<select>` box hierarchies blocking scraping algorithms randomly.
*   Coupons configured as "Percent value" will sometimes require calculating against base-prices, meaning edge-caches occasionally read `None` as the effective `coupon_value` if the base price gets hidden.
*   The Redis Deduplication relies on Windows installations. If no `.env` value is verified or Redis isn't operating on Port `6379` natively, the platform will silently fall back bypassing Deduplication limits seamlessly.
