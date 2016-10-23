#!/usr/bin/env python3

"""main.py allows you to start the scraper."""

import datetime
from scraper import HoldingsScraper
import sys

ticker = ''
while len(ticker) < 1:
    ticker = input('Please enter a ticker: ')

sys.stdout.write('Scraping started at %s\n' % str(datetime.datetime.now()))
holdings = HoldingsScraper(ticker)
holdings.scrape()

try:
    holdings.remove_temp_file()
except:
    pass

sys.stdout.write('Scraping completed at %s\n' % str(datetime.datetime.now()))