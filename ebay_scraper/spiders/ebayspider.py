import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ebay_scraper.items import EbayItem, EbayItemLoader


class EbaySpider(CrawlSpider):
    name = "ebay_scraper"
    allowed_domains = ["ebay.com"]

    # Allow a custom parameter (-a flag in the scrapy command)
    def __init__(self, search="Philips 27 inch Monitor", start_page=1, *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs)
        self.search_string = search
        self.start_urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={self.search_string.replace(' ', '+')}&_ipg=240&&_sacat=0&_pgn={start_page}"]
    

    # Define the rules for crawling:
    rules = (
        Rule(
            LinkExtractor(
                restrict_css='ol.pagination__items li a',
                deny=(r"#",),  # Exclude any links ending with #
            ),
            
        ),
        Rule(
            LinkExtractor(
                restrict_css='li a.s-item__link',
                deny=(r"#",)  # Exclude any links ending with #
            ),
            callback='parse_product_page',  # Callback for product details page
            )
        )

    def parse_product_page(self, response):
        about_this_item = response.css("div.tabs")
        last_update = about_this_item.xpath(".//div[contains(text(), 'Last updated on')]/following-sibling::div").get('')
        item_spesifics = about_this_item.css("div[class*='ux-layout-section-module-evo']")
        condition_block = item_spesifics.css("dl[class$='--condition']")
        condition = condition_block.css("dd span.ux-textspans").get('')
        brand_block = item_spesifics.css("dl[class$='--brand']")
        brand = brand_block.css("dd span").get('')
        upcc_block = item_spesifics.css("dl[class$='--upc']")
        upcc = upcc_block.css("span.ux-textspans").get('')

        right_panel =response.css("div[id*='RightSummaryPanel']")
        name = right_panel.css("h1[class*='x-item-title__mainTitle'] > span:nth-of-type(1)").get('')
        price = right_panel.css("div[class*='x-price-primary'] > span:nth-of-type(1)").get('')
        availability = right_panel.css("div[id*='qtyAvailability'] > span:nth-of-type(1)").get('')
        shipping_cost = right_panel.xpath("span[contains(text(), 'Shipping')]/ancestor::div[3]//span[contains(@class, 'ux-textspans ux-textspans--BOLD')]").get('')
        location = right_panel.xpath("span[contains(text(), 'Shipping')]/ancestor::div[3]//span[contains(@class, 'ux-textspans ux-textspans--SECONDARY')]").get('')
        store_info_block = response.css("div#STORE_INFORMATION")
        highlights = store_info_block.css("h4.x-store-information__highlights")
        feedback =highlights.xpath(".//span[contains(text(), 'Feedback')]").get('')
        items_sold = highlights.css("span[class$='SECONDARY']").get('')
        no_of_feedbacks = store_info_block.css("h2[class*='fdbk-detail-list__title'] span.SECONDARY").get('')

        rating_block = response.css("div[data-testid*='ux-summary' ] span")
        rating = rating_block.css("span.ux-textspans").get('')
        rating_count = rating_block.css("span.ux-summary__count").get('')

        loader = EbayItemLoader(item=EbayItem())

        loader.add_value('name', name)
        loader.add_value('price', price)
        loader.add_value('availability', availability)
        loader.add_value('shipping_cost', shipping_cost)
        loader.add_value('location', location)
        loader.add_value('last_update', last_update)
        loader.add_value('condition', condition)
        loader.add_value('brand', brand)
        loader.add_value('upcc', upcc)
        loader.add_value('feedback', feedback)
        loader.add_value('no_of_feedbacks', no_of_feedbacks)
        loader.add_value('items_sold', items_sold)
        loader.add_value('rating', rating)
        loader.add_value('rating_count', rating_count)
        loader.add_value('product_url', response.url)

        yield loader.load_item()