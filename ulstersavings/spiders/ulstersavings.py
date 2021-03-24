import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ulstersavings.items import Article


class UlstersavingsSpider(scrapy.Spider):
    name = 'ulstersavings'
    start_urls = ['https://www.ulstersavings.com/why-us/news-and-blog/']

    def parse(self, response):
        links = response.xpath('//div[@class="col-sm-9"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[span[text()="Next Page"]]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="col-sm-9"]/p[2]/text()').get()
        if date:
            date = " ".join(date.split()[1:])

        content = response.xpath('//div[@class="col-sm-9"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
