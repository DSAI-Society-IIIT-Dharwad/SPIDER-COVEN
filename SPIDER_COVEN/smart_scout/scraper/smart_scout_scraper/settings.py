import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../.env')

BOT_NAME = "smart_scout_scraper"
SPIDER_MODULES = ["smart_scout_scraper.spiders"]
NEWSPIDER_MODULE = "smart_scout_scraper.spiders"

# ScrapeOps proxy (IP rotation)
SCRAPEOPS_API_KEY = os.getenv("SCRAPEOPS_API_KEY", "your-key")
SCRAPEOPS_PROXY_ENABLED = False
SCRAPEOPS_PROXY_SETTINGS = {"country": "in"}

# Middleware order
DOWNLOADER_MIDDLEWARES = {
    # "scrapeops_scrapy_proxy_sdk.scrapeops_scrapy_proxy_sdk.ScrapeOpsScrapyProxySdk": 725,
    "smart_scout_scraper.middlewares.TLSDownloaderMiddleware": 100,
    "smart_scout_scraper.middlewares.LocationMiddleware": 750,
    "smart_scout_scraper.middlewares.RotateUserAgentMiddleware": 400,
}

ITEM_PIPELINES = {
    "smart_scout_scraper.pipelines.ValidationPipeline": 100,
    "smart_scout_scraper.pipelines.HoneypotFilterPipeline": 150,
    "smart_scout_scraper.pipelines.DeduplicationPipeline": 200,
    "smart_scout_scraper.pipelines.DatabasePipeline": 300,
}

# Throttle
DOWNLOAD_DELAY = 2
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Retry
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 429, 500, 503]

# Playwright
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
FEED_EXPORT_ENCODING = "utf-8"
