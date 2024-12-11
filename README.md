# scraper
This project is a web scraper designed to extract detailed product information from eBay using the Scrapy framework. It enables users to gather structured data from eBay product listings dynamically based on a search query.

Features
Dynamic Search: Specify a custom search query and start scraping from a desired page using Scrapy's -a flag.
Pagination Support: Automatically follows pagination links to scrape multiple pages of search results.
Product Details Extraction: Extracts comprehensive details such as:
Product name, price, availability, shipping cost, and location.
Product specifics like brand, UPC, and item attributes.
Ratings, feedback, and seller information.
Images and their URLs.
Dynamic Fields Handling: Automatically detects and processes custom fields (e.g., item specifics) dynamically for each product.
Extensibility: The project employs dynamic item generation, making it adaptable to varying structures of eBay product pages.
Requirements
To use this project, ensure you have the following installed:

Python 3.8+
Scrapy
w3lib
Other dependencies listed in requirements.txt (if applicable)
Installation
Clone this repository:

bash
Copy code
git clone https://github.com/yourusername/ebay-scraper.git
cd ebay-scraper
Create and activate a virtual environment (optional but recommended):

Usage
Run the scraper with the desired search query and starting page. Example:

bash
Copy code
scrapy crawl ebay_scraper -a search="Wireless pc keyboard" -a start_page=1 -o output.json
Command-Line Parameters
search: The search query (e.g., "Wireless pc keyboard").
start_page: The page number to start scraping from (default: 1).
The scraped data will be saved in the specified output file (output.json in the example above).

Project Structure
ebay_scraper/spiders/ebay_spider.py: Contains the main spider logic.
ebay_scraper/items.py: Defines item loaders and dynamic item generation logic.
ebay_scraper/pipelines.py: (Optional) Include custom pipelines for post-processing.
ebay_scraper/settings.py: Scrapy settings for the project.
Key Components
Spider: EbaySpider
Crawls eBay search result pages and follows links to product details pages.
Uses rules with Scrapy's CrawlSpider for structured navigation.
Dynamic Item Generation
The DynamicEbayItemGenerator dynamically creates Scrapy Item classes based on the fields available on the eBay product page.
Item Loader: EbayItemLoader
Handles input and output processing for extracted fields.
Includes custom processors like replace_chars, get_stars, and get_location for data cleaning.
Output
The scraped data includes:

Standard fields: name, price, availability, shipping_cost, location, etc.
Dynamic fields: Product-specific attributes extracted from the eBay listing.
Customization
Extend the spider by adding more CSS or XPath selectors to capture additional information.
Modify item loaders or processors to handle specific data transformations.
License
This project is licensed under the MIT License. See the LICENSE file for more details.

Contributions
Contributions, issues, and feature requests are welcome! Feel free to fork this repository and submit a pull request.


