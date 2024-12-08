# -*- coding: utf-8 -*-
import scrapy
import re

class EbaySpider(scrapy.Spider):
	
	name = "ebay_scraper"
	allowed_domains = ["ebay.com"]
	start_urls = ["https://www.ebay.com"]

	# Allow a custom parameter (-a flag in the scrapy command)
	def __init__(self, search="nintendo switch console"):
		self.search_string = search

	def parse(self, response):
		# Extrach the trksid to build a search request	
		trksid = response.css("input[type='hidden'][name='_trksid']").xpath("@value").getall()[0]       
		
		# Build the url and start the requests
		yield scrapy.Request("http://www.ebay.com/sch/i.html?_from=R40&_trksid=" + trksid +
							 "&_nkw=" + self.search_string.replace(' ','+') + "&_ipg=240" +
							 "&_pgn=1", 
							 callback=self.parse_link)

	# Parse the search results
	def parse_link(self, response):
		# Extract the list of products 
		results = response.xpath('//ul[contains(@class, "srp-results")]/li[contains(@class, "s-item" )]')

		# Extract info for each product
		for product in results:		
			name = product.xpath('.//*[@class="s-item__title"]//text()').get()		
			# # If this get a None result
			if name == None:
				name = "Not found |:-("

			price = product.xpath('.//*[@class="s-item__price"]/text()').get()
			status = product.xpath('.//*[@class="SECONDARY_INFO"]/text()').get()
			seller_level = product.xpath('.//*[@class="s-item__etrs-text"]/text()').get()
			location = product.xpath('.//*[@class="s-item__location s-item__itemLocation"]/text()').get()
			product_url = product.xpath('.//a[@class="s-item__link"]/@href').get()

			# Set default values
			stars = 0
			ratings = 0

			stars_text = product.xpath('.//*[@class="clipped"]/text()').get()
			if stars_text: stars = stars_text[:3]
			ratings_text = product.xpath('.//*[@aria-hidden="true"]/text()').get()
			if ratings_text: ratings = ratings_text.split(' ')[0]

			summary_data = {
							"Name":name,
							"Status":status,
							"Price":price,
							"Stars":stars,
							"Ratings":ratings,
							"URL": product_url
							}

			# Go to the product details page
			data = {'summary_data': summary_data}
			yield scrapy.Request(product_url, meta=data, callback=self.parse_product_details)

		# Get the next page
		next_page_url = response.xpath('//*/a[@class="pagination__next icon-link"]/@href').get()

		# The last page do not have a valid url and ends with '#'
		if next_page_url == None or response.css("h1.srp-controls__count-heading span::text").get() == '0':
			self.log("eBay products collected successfully !!!")
		else:
			yield scrapy.Request(next_page_url, callback=self.parse_link)


	# Parse details page for each product
	def parse_product_details(self, response):

		# Get the summary data
		data = response.meta['summary_data']

		# Add more data from details page
		data['UPC'] = response.xpath('//h2[@itemprop="gtin13"]/text()').get()

		yield data




