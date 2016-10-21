import datetime
from scraper import HoldingsScraper
import sys

# Hershey Trust '0000908551'
# Menlo Advisors '0001279708'
# BlackRock '0001086364'
# Gates Foundation '0001166559'

ticker = ''
while len(ticker) < 1:
    ticker = input('Please enter a ticker: ')
sys.stdout.write('Scraping started at %s\n' % str(datetime.datetime.now()))
holdings = HoldingsScraper(ticker)
holdings.scrape()