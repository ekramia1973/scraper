import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ebay_scraper.items import EbayItemLoader
from ebay_scraper.items import remove_tags, replace_chars
from itemloaders.processors import MapCompose, TakeFirst
from ebay_scraper.items import DynamicEbayItemGenerator
# from icecream import ic

class EbaySpider(CrawlSpider):
    name = "ebay_scraper"
    allowed_domains = ["ebay.com"]
    page_no = None
    # Allow a custom parameter (-a flag in the scrapy command)
    def __init__(self, search="Wireless pc keyboard", start_page=1, *args, **kwargs):
        super(EbaySpider, self).__init__(*args, **kwargs)
        self.search_string = search
        self.start_urls = [f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw={self.search_string.replace(' ', '+')}&_ipg=240&&_sacat=0&_pgn={start_page}"]
        
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
        
        brand_block = item_spesifics.css("dl[class$='--brand']")
        brand = brand_block.css("dd span").get('')
        upcc_block = item_spesifics.css("dl[class$='--upc']")
        upcc = upcc_block.css("span.ux-textspans").get('')

        right_panel =response.css("div[id*='RightSummaryPanel']")
        name = right_panel.css("h1[class*='x-item-title__mainTitle'] > span").get('')
        price = right_panel.css("div[class*='x-price-primary'] > span:nth-of-type(1)").get('')
        availability = right_panel.css("div[id*='qtyAvailability'] > span:nth-of-type(1)").get('')
        shipping_cost = right_panel.xpath("span[contains(text(), 'Shipping')]/ancestor::div[3]//span[contains(@class, 'ux-textspans ux-textspans--BOLD')]").get('')
        location = right_panel.xpath("span[contains(text(), 'Shipping')]/ancestor::div[3]//span[contains(@class, 'ux-textspans ux-textspans--SECONDARY')]").get('')

        store_info_block = response.css("div#STORE_INFORMATION")
        highlights = store_info_block.css("h4.x-store-information__highlights")
        feedback =highlights.css("h4 > span").get('')
        items_sold = highlights.css("span[class$='SECONDARY']").get('')
        no_of_feedbacks = store_info_block.css("h2[class*='fdbk-detail-list__title'] span.SECONDARY").get('')
        contact_seller = store_info_block.xpath("//span[contains(text(), 'Contact')]/ancestor::a[1]/@href").get('')

        images_array = response.css("div[class='ux-image-carousel-container image-container'] div[tabindex='0'] img")
        images_urls = []
        for img in images_array:
            images_urls.append(
                img.css("img::attr(data-src)").get('') or img.css("img::attr(src)").get('')
                )

        rating_block = response.css("div[class$='ux-summary'] ")
        rating = rating_block.css("span.ux-summary__start--rating > span").get('')
        rating_count = rating_block.css("span.ux-summary__count > span").get('')

        product_url = response.url

        item_spesifics_block_rows = response.css("div.vim.x-about-this-item .ux-layout-section-evo__row")
        columns = dict()
        input_processor = MapCompose(remove_tags, replace_chars, str.strip)
        for row in item_spesifics_block_rows:
            for col in row.css("div.ux-layout-section-evo__col"):
                col_title = TakeFirst()(input_processor(col.css("dt").get()))
                # col_description = TakeFirst()(input_processor(col.css("dd").get()))
                col_description = col.css("dd").get()
                if col_title:
                    columns[col_title] = col_description 

        field_names = [
                        "name",
                        "price",
                        "availability",
                        "shipping_cost",
                        "location",
                        "last_update",
                        "brand",
                        "upcc",
                        "feedback",
                        "items_sold",
                        "no_of_feedbacks",
                        "contact_seller",
                        "images_urls",
                        "rating",
                        "rating_count",
                        "product_url"
                    ]
        
        # extend the field_names array with dynamically extracted field names
        for col_title in columns.keys():
            field_names.append(col_title)
        
        DynamicEbayItem = DynamicEbayItemGenerator(field_names)   

        loader = EbayItemLoader(item=DynamicEbayItem(), selector=response)
        # add values to the loader till the dynamic rows start
        for field_name in field_names[:(-len(columns.keys()))]:  
            loader.add_value(field_name, locals().get(field_name))

        # append the dynamic rows to the fields
        for col_title, col_description in columns.items():
            loader.add_value(col_title, col_description)


        yield loader.load_item()