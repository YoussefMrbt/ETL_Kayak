# Import necessary libraries and modules
# Import os => Library used to easily manipulate operating systems
import os 
# Import logging => Library used for logs manipulation 
import logging
import json  # To handle JSON data

from argparse import ArgumentParser # To parse command-line arguments

# Import scrapy and scrapy.crawler 
import scrapy

from scrapy.crawler import CrawlerProcess # For initializing the crawl process
from scrapy.utils.project import get_project_settings # To access and modify project settings
from scrapy.exceptions import CloseSpider # To trigger an exception that stops the spider

# Define the BookySpider class that extends scrapy.Spider
# This spider is customized for scraping booking.com hotel data
class BookySpider(scrapy.Spider):
    name = 'Bookyspidy'
    # Define your custom User-Agent here
    custom_user_agent = 'MyCustomUserAgent/1.0' # Define a custom User-Agent for this spider
    
    # Initialize the spider with optional arguments for form data and output filename
    def __init__(self, *args, **kwargs):
        super(BookySpider, self).__init__(*args, **kwargs)
        self.formdata = kwargs.get('formdata', {})
        self.filename = kwargs.get('filename', 'output.csv') # Default filename if not provided
        
    # Override the from_crawler class method to configure feed export settings dynamically
    @classmethod    
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BookySpider, cls).from_crawler(crawler, *args, **kwargs)
        # Set feed export format and filename if 'filename' parameter is passed
        if 'filename' in kwargs:
            settings = get_project_settings()
            settings.set('FEEDS', {'source/' + kwargs['filename']: {"format": "csv"}})
        return spider
    
    # The start_requests method generates the initial request for the spider
    def start_requests(self):
        # Send a GET request to the booking.com home page with the custom User-Agent
        yield scrapy.Request(url='https://www.booking.com', headers={'User-Agent': self.custom_user_agent}, callback=self.parse)
    
    # Parse the initial response to submit a search form with provided form data
    def parse(self, response):
        # Use the provided form data to submit the search request using a form request
        return scrapy.FormRequest.from_response(
            response,
            formxpath='//input[@name="ss"]',  #XPath to locate the search input element
            formdata=self.formdata,  #The value to input into the search input element
            callback=self.after_search # Define the next callback action
        )
    
    # Handle the search results page and yield requests for individual hotel pages    
    def after_search(self, response):
        # Define control variables for iterating over search results
        n = 55  # Presumably the number of results to scrape, higher than actual number in order to not miss
        p = 0   # A counter for missing hotel names or URLs
        self.logger.info("REACHED AFTER SEARCH")
        
        #For loop to gather hotel name and hotel url
        for i in range(3, n+1, 1):
            #try-except block to handle errors
            try:
                hotel_elem = response.xpath('//*[@id="search_results_table"]/div[2]/div/div/div[3]/div[{}]/div[1]/div[2]/div/div/div/div[1]/div/div[1]/div/h3/a'.format(i)) #main Xpath
                hotel_name = hotel_elem.xpath('div[1]/text()').get() #Hotel name Xpath
                hotel_url = hotel_elem.xpath('@href').get()  #Hotel url Xpath

                #If value found, then launch new request to go into the hotel page
                if hotel_name and hotel_url:
                    yield scrapy.Request(url=hotel_url, headers={'User-Agent': self.custom_user_agent},  #request into hotel url
                        callback=self.after_url, #Define next callback action
                        meta={'hotel_name': hotel_name, 'hotel_url': hotel_url}) #Meta, to use variable in after_url
                    
                else:
                    #If value not found, then print an error and counter +1
                    self.logger.info(f"Hotel name or URL missing at index {i}.")
                    p += 1
                
                #When counter is too high then close the spider and print error, print formdata into fails.json1 through save_to_fail_log
                if p == 30 and hotel_url is None:
                    self.logger.error("No URL found,  saving to fails.json")
                    self.save_to_fail_log(self.formdata)
                    raise CloseSpider('URL missing, stopping the spider.')
                    # The spider will stop after the exception is raised.
                        
            except Exception as e:
                self.logger.error(f"Error at index {i}: {e}")
                
    #Handle searching hotel information            
    def after_url(self, response):
        hotel_name = response.meta.get('hotel_name') #Retrieving hotel name
        hotel_url = response.meta.get('hotel_url') #Retrieving hotel url
        self.logger.info('REACHED AFTER URL') #Print to track progress
        
        #try-except block to handle errors
        try:
            description = response.xpath('//*[@id="property_description_content"]/div/p/text()').get() #hotel description
            score = response.xpath('//*[@id="basiclayout"]/div[1]/div[10]/div/div[3]/div/div[2]/div/button/div/div/div[1]/text()').get() #Hotel score
            rev = response.xpath('//*[@id="basiclayout"]/div[1]/div[10]/div/div[3]/div/div[2]/div/button/div/div/div[2]/span[2]/text()[2]').get() #Hotel review

            #Alternative if could not find the score
            if score:
                pass
            else:
                score = response.xpath('//*[@id="basiclayout"]/div[1]/div[10]/div/div[5]/div/div/header/div[2]/div[1]/span[1]//text()').get()
            
            #Alternative if could not find the review
            if rev:
                pass
            else:
                rev = response.xpath('//*[@id="basiclayout"]/div[1]/div[10]/div/div[5]/div/div/header/div[2]/div[1]/span[2]/text()[1]').get()
                
            #Finding the hotel latitude and longitude
            latlon = response.xpath('//a[@id="hotel_sidebar_static_map"]/@data-atlas-latlng').get()
        
            if latlon:
                # Splitting the string into latitude and longitude
                lat, lon = latlon.split(',')

            #Results in the form of a dictionary, if no value then None
            yield {
                "hotel_name": hotel_name.strip() if hotel_name else None,  # Use strip to remove whitespace
                "hotel_score": score.strip() if score else None,
                "hotel_reviews": rev.strip() if rev else None,
                "hotel_lat": lat.strip() if lat else None,
                "hotel_lon": lon.strip() if lon else None,
                "hotel_url": hotel_url.strip() if hotel_url else None,
                "hotel_description": description.strip() if description else None,
            }

        except Exception as e:
            self.logger.error(f"Error after url: {e}")
    
    #Handle the saving of fails into fail file            
    def save_to_fail_log(self, formdata, filename="fails.jsonl"):
        # Ensure that formdata is a dictionary
        if isinstance(formdata, dict):
            # Open the file in append mode, which allows you to add new entries without overwriting existing ones
            with open(filename, 'a') as file:
                # Write the formdata as a JSON string followed by a new line character to the file
                file.write(json.dumps(formdata) + '\n')
        else:
            self.logger.error("Formdata is not a dictionary.")
                
                
# Define the command-line argument parser to configure the spider run
parser = ArgumentParser(description="Scrapy Booking Spider")

# Add command-line arguments for formdata and filename
parser.add_argument('-f', '--formdata', help='Form data as a JSON string', required=True)
parser.add_argument('-o', '--filename', help='Output filename with .csv extension', required=True)

# Execute the parse_args method to retrieve arguments passed to the script
args = parser.parse_args()

# The formdata argument is expected to be a JSON string, so parse it into a dictionary
formdata = json.loads(args.formdata)

# Configure a new CrawlerProcess with the custom settings for User-Agent and output format
process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0', # Define a default user agent for all requests
    'LOG_LEVEL': logging.INFO, # Set the logging level to INFO to reduce console output clutter
    "FEEDS": {      # Configure output feed settings specifying path, format, and fields
        os.path.join('source', args.filename): {
            "format": "csv",
            "encoding": "utf8",  # Ensure utf8 encoding for compatibility
            "fields": ['hotel_name', 'hotel_score', 'hotel_reviews', 'hotel_lat', 'hotel_lon', 'hotel_url', 'hotel_description'],  # Optional: Specify the order of fields
        },
    },
})

# Start the spider by passing the formdata and filename as arguments
# 'formdata' is used to populate the search query, and 'filename' sets the CSV output destination
process.crawl(BookySpider, formdata=formdata, filename=args.filename)

# Start the crawling process
process.start()