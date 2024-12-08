
from scrapy.loader import ItemLoader
from scrapy import Item, Field
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags
import re

def replace_chars (text):
    for char in ['\n', '\r', '\t', '\\']:
        text = text.replace(char, '')
    return text
def get_stars(stars_text=''):
    if stars_text:
        match = re.match(r"^\d+(\.\d+)?", stars_text)
        stars = match.group(0) if match else ''
    return ''
def get_location(location_text):
    if 'from' in location_text:
        return location_text.split('from ')[1]
    else:
        return location_text
def set_default(value):
    if not value:
        return ''
    else:
        return value

class EbayItem(Item):
    name = Field()
    price = Field()    
    availability = Field()    
    shipping_cost = Field()
    location = Field()
    last_update = Field()
    condition = Field()
    brand = Field()
    upcc = Field()
    feedback = Field()
    items_sold = Field()    
    no_of_feedbacks = Field()
    rating = Field()
    rating_count = Field()
    product_url = Field()

    
class EbayItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    default_input_processor = MapCompose(str.strip, remove_tags, replace_chars)