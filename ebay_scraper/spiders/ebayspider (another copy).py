import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ebay_scraper.items import EbayItem, EbayItemLoader


class EbaySpider(CrawlSpider):
    name = "ebay_scraper"
    allowed_domains = ["ebay.com"]
    start_urls = ["https://www.ebay.com"]

    # Allow a custom parameter (-a flag in the scrapy command)
    def __init__(self, search="Philips 27 inch Monitor", *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs)
        self.search_string = search

    # Define the rules for crawling:
    rules = (
        Rule(
            LinkExtractor(
                allow=r"/sch/i.html\?(_from=R40&)?_trksid=.*&_nkw=.*&_ipg=.*&_pgn=\d+",  # URL pattern for search and pagination
                deny=(r"#",)  # Exclude any links ending with #
            ),
            callback='parse_link',  # Same callback for both pagination and product pages
            follow=True  # Follow pagination links (follow=True to continue crawling)
        ),
    )

    def parse_start_url(self, response):
        # Extract the trksid from the start page
        trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").get()
        if not trksid:
            trksid = "m570.l1313"
        # Build the search URL using the search term and start crawling
        search_url = f"https://www.ebay.com/sch/i.html?_from=R40&_trksid={trksid}&_nkw={self.search_string.replace(' ', '+')}&_ipg=240&_pgn=1"
        yield scrapy.Request(search_url, callback=self.parse_link)

    def parse_link(self, response):
        # Extract the list of products
        results = response.xpath('//ul[contains(@class, "srp-results")]/li[contains(@class, "s-item")]')
        
        # Extract info for each product
        for product in results:
            loader = EbayItemLoader(item=EbayItem(), selector=product)

            loader.add_xpath('name', './/div[@class="s-item__title"]/span')
            loader.add_xpath('price', './/span[contains(@class, "s-item__price")]')
            loader.add_xpath('status', './/*[@class="SECONDARY_INFO"]')
            loader.add_xpath('seller_level', './/span[@class="s-item__etrs-text"]')
            loader.add_xpath('location', './/*[@class="s-item__location s-item__itemLocation"]')
            loader.add_css('stars', 'div.x-star-rating span.clipped')
            loader.add_css('ratings', 'span[aria-hidden="false"]')
            loader.add_css('product_url', 'a.s-item__link ::attr(href)')

            yield scrapy.Request(loader.get_output_value('product_url'),
                                  callback=self.parse_product_details, 
                                  meta={'loader': loader})

    def parse_product_details(self, response):
        loader = response.meta['loader']
        loader.add_xpath('availability', '//div[@id="qtyAvailability"]/span[1]')
        loader.add_xpath('item_number', '//span[contains(text(),"eBay item number:")]/following-sibling::span')

        yield loader.load_item()