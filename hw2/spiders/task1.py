'''
Matheus Schmitz
DSCI 558 | Building Knowledge Graphs
Homework 1
'''

# Imports
import scrapy
import datetime
import re
import csv

class Crawler(scrapy.Spider):

	# Crawler name, which has to be called when running the script: scrapy crawl task1 -o task1.csv
	name = 'task1'

	# Define the IMDB page listing all actors as the start page
	start_urls = ['https://www.imdb.com/search/name/?birth_monthday=01-30']
	allowed_domains = ['imdb.com']

	# Set the number to pages to crawl before stopping, and slow the scraper not to get banned
	custom_settings = {'CLOSESPIDER_ITEMCOUNT': 1000,
	              	 'DOWNLOAD_DELAY': 1.000,
	              	 'CONCURRENT_ITEMS': 500,
	              	 'CONCURRENT_REQUESTS': 100,
	              	 'FEEDS': 'csv'}

	def parse(self, response):	


		# Find the 50 blocks per page containing celebrity info
		celebrity_blocks = response.css('.lister-item-content')

		# For each block having celebrity info do:
		for celebrity in celebrity_blocks:

		    # Get the celebrity page ID
		    self.celebrity_id = celebrity.css('a::attr(href)').get()

		    # Build a html link with the celebrity's page ID
		    celebrity_page = 'https://www.imdb.com' + self.celebrity_id

		    # Request that page and pass it to the find_biography
		    celebrity_details = scrapy.Request(url=celebrity_page, callback=self.find_biography)

		    # Then output a json (dict) to the linked json (.jl) file
		    yield  celebrity_details

		# Once all 50 celebrity blocks have been parsed, find the html link for the next page
		page_link = response.xpath('//*[@id="main"]/div/div[1]/a[@class="lister-page-next next-page"]/@href').get()

		# Build a full html with the link for the next page
		next_page = 'https://www.imdb.com' + page_link

		# "Click" the link by following it with a looped-callback to self
		yield response.follow(url=next_page, callback=self.parse)
    

	def find_biography(self, response):

		# Find the link to the full bio page
		bio_link = response.xpath('//*[@id="name-bio-text"]/div/div/span/a/@href').get()

		# Build the html link for the bio page
		bio_page = 'https://www.imdb.com' + bio_link

		# Send the page to the biography_parser
		biography = scrapy.Request(url=bio_page, callback=self.biography_parser)

		return biography


	def biography_parser(self, response):

		# Find the biography text
		try:
			bio_text = response.xpath('//*[@id="bio_content"]/div[2]/p[1]//text()').getall()
			bio_text = ''.join(bio_text).strip()
		except:
			pass

		# Write to the csv file
		return {'url': str(response.url),
				'bio': bio_text}

'''
For CSV outputting this script requires a file exporters.py on the parent folder from the spiders folder (which is this folder)

The exporters.py file needs the following code:


from scrapy.exporters import CsvItemExporter
class HeadlessCsvItemExporter(CsvItemExporter):

    def __init__(self, *args, **kwargs):

        # args[0] is (opened) file handler
        # if file is not empty then skip headers
        if args[0].tell() > 0:
            kwargs['include_headers_line'] = False

        super(HeadlessCsvItemExporter, self).__init__(*args, **kwargs)


Additonally, the settings.py file needs the following code:

FEED_EXPORTERS = {
    'csv': 'hw2.exporters.HeadlessCsvItemExporter',
}
'''