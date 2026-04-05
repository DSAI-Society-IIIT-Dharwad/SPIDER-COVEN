import scrapy

class PriceItem(scrapy.Item):
    asin            = scrapy.Field()
    title           = scrapy.Field()
    seller          = scrapy.Field()
    price           = scrapy.Field()
    shipping        = scrapy.Field()
    total_price     = scrapy.Field()
    net_price       = scrapy.Field()
    coupon_value    = scrapy.Field()
    is_buy_box      = scrapy.Field()
    is_fba          = scrapy.Field()
    is_suspicious   = scrapy.Field()
    pin_code        = scrapy.Field()
    dominance_score = scrapy.Field()
    stock_left      = scrapy.Field()
    scraped_at      = scrapy.Field()
