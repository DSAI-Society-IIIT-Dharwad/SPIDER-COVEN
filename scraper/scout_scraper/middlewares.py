from curl_cffi import requests as cr

class LocationMiddleware:
    """Inject delivery pincode cookie to simulate regional buyers."""

    def process_request(self, request, spider):
        pin = request.meta.get("pin_code", "600001")
        # Confirm this cookie key by inspecting Chrome DevTools on amazon.in
        # Application → Cookies → amazon.in → look for delivery-zip-code
        request.cookies["delivery-zip-code"] = pin
        request.headers["Accept-Language"] = "en-IN,en;q=0.9"
        return None

class TLSDownloaderMiddleware:
    """Replace Scrapy's default downloader with curl_cffi for TLS fingerprinting."""

    def process_request(self, request, spider):
        if request.meta.get("playwright"):
            return None   # let Playwright handle JS pages
        try:
            pin = request.meta.get("pin_code", "600001")
            resp = cr.get(
                request.url,
                impersonate="chrome120",
                headers=dict(request.headers),
                cookies={"delivery-zip-code": pin},
                timeout=15
            )
            from scrapy.http import HtmlResponse
            return HtmlResponse(
                url=request.url,
                body=resp.content,
                encoding="utf-8",
                request=request
            )
        except Exception as e:
            spider.logger.warning(f"curl_cffi failed: {e} — falling back")
            return None
