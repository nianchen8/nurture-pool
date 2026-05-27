import scrapy


class BaiduSpider(scrapy.Spider):
    name = "baidu"
    start_urls = ["https://www.baidu.com"]

    def parse(self, response):
        yield {
            "url": response.url,
            "status": response.status,
            "title": response.css("title::text").get(),
            "ua_sent": response.request.headers.get("User-Agent", b"").decode(),
        }
