
from scrapy.loader import ItemLoader
from scrapy import Item, Field
from itemloaders.processors import TakeFirst, MapCompose, Identity, Compose
from w3lib.html import remove_tags
import re

def replace_chars (text):
    # remove any starting and endingparanthesis, 
    # together with newlines, tabs, and backslashes
    return re.sub(r"^[\(]|[\n\r\t\\]|[\)]$", "", text)
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

class EbayItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    default_input_processor = MapCompose(str.strip, remove_tags, replace_chars)

def DynamicEbayItemGenerator(field_names):
    # Creates a dynamic Scrapy Item class with the given field names.

    # Define the fields dictionary dynamically
    fields = {field_name: Field() for field_name in field_names}
    # define the output processor for the images_urls field since it shall return a list
    fields.get('images_urls').output_processor = Identity()

    # fields.get("no_of_feedbacks").input_processor = Compose(
    #     MapCompose(replace_chars, str.strip)
    # )

    # Use type to dynamically create the Item class
    dynamic_item_class = type("DynamicEbayItem", (Item,), fields)
    return dynamic_item_class
    
