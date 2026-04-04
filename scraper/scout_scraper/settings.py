BOT_NAME = "scout_scraper"
SPIDER_MODULES = ["scout_scraper.spiders"]

# ScrapeOps proxy (IP rotation)
SCRAPEOPS_API_KEY = "your-key"
SCRAPEOPS_PROXY_ENABLED = True
SCRAPEOPS_PROXY_SETTINGS = {"country": "in"}

# Middleware order
DOWNLOADER_MIDDLEWARES = {
    "scrapeops_scrapy.scrapeops_scrapy.ScrapeOpsScrapyProxyMiddleware": 725,
    "scout_scraper.middlewares.LocationMiddleware": 750,
    "scout_scraper.middlewares.RotateUserAgentMiddleware": 400,
}

ITEM_PIPELINES = {
    "scout_scraper.pipelines.ValidationPipeline": 100,
    "scout_scraper.pipelines.DeduplicationPipeline": 200,
    "scout_scraper.pipelines.DatabasePipeline": 300,
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
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"