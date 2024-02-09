
# Project Kayak

## Overview

Project Kayak is a scholar project aimed at providing travelers with comprehensive travel planning insights by integrating weather information and accommodation options for cities worldwide. Utilizing data from the OpenWeatherMap API and scraping accommodation details from Booking.com, this project offers an unparalleled tool for identifying ideal travel destinations and accommodations based on weather conditions and hotel ratings.

## Project Structure

Weather Data Collection Notebook: A Jupyter notebook that fetches and processes meteorological data for multiple cities using the OpenWeatherMap API. This notebook is the first step in our two-part data collection process, focusing on gathering current weather conditions to aid in the travel planning process.

Accommodation Data Collection Script: A two-step Scrapy script designed to scrape Booking.com for the best hotels in each city. The script operates in phases:

- Phase 1: Collects initial hotel data from the first page of search results for each city and saves it to a CSV file.
- Phase 2: Appends detailed information from the second page of search results to the CSV, enriching the dataset with comprehensive accommodation options.
- Data Visualization and Analysis Notebook: This notebook loads the combined weather and accommodation data into a DataFrame for analysis. It features:
- Weather Ranking Map: A world map visualization ranking cities based on their current weather conditions, providing a global overview of ideal travel destinations.
- Hotel Visualization Map: For a selected city, this map displays the top hotels based on the scraped Booking.com data, offering insights into the best accommodation options.
- Data Aggregation and Storage: The final step involves aggregating the collected data into a larger database format, which is then stored in an Amazon S3 bucket for persistence and future accessibility.

## Automated Retry Mechanism for Failed Scrapes

"Project Kayak" features an advanced automated process for managing and retrying failed scrapes during the accommodation data collection phase. This process is designed to ensure comprehensive data collection by automatically addressing failures without manual intervention. Here’s how it works:

### Automated Failure Handling and Retries

Automatic Logging of Failures: If a scrape attempt fails, the script automatically logs the failure details (such as the city name) into a fails.json file. This file serves as a dynamic record of scrapes that need to be retried.

### Retry Process: Upon finishing the list of hotel to scrap, the script initiates a retry mechanism by rescraping the list from the fails.json file, emptying at the same time and record again the fails in the same file in case.

Emptying the fails.json File: The retry process is recursive and continues until all failed attempts have been successfully retried and the fails.json file is left empty. This ensures that every intended data point is collected, and the dataset is as complete as possible.

## Getting Started

Prerequisites
Python 3.6+
Jupyter Notebook
Scrapy
Pandas
Plotly
Boto3 (for AWS S3 integration)

API Keys: Ensure you have an API key for OpenWeatherMap and AWS credentials configured for accessing S3.

## Running the Project

Weather Data Collection: Open the weather data collection notebook in Jupyter and execute the cells to fetch and process weather data.

## Accommodation Data Scraping:

Navigate to the Scrapy script directory.
Run the script with Scrapy to collect hotel data for the cities of interest.
Data Visualization and Analysis: Open the data visualization notebook in Jupyter, load the collected data, and generate the interactive maps.

Data Aggregation and Storage: Follow the instructions in the notebook to aggregate the data and upload it to an S3 bucket.

## Contributing

We welcome contributions to Project Kayak. If you have suggestions for improvements or encounter any issues, please open an issue first to discuss what you would like to change.
