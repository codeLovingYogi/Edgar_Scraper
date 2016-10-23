#!/usr/bin/env python3

"""
main.py allows you to start the scraper. 

This program uses Python3, Selenium, PhantomJS, 
BeautifulSoup, and lmxl.

Before using the scraper:
1. Check that you have Python 3:
    python3 --version
2. Create a virtual environment in Python
    ie. python3 -m venv myvenv
3. Activate virtual environment
    ie. source myvenv/bin/activate
4. Install requirements.txt
    pip install -r requirements.txt
5. Install PhantomJS (if not already installed)

To start scraper, run in an activated 
virtual environment, the command: 'python main.py'

Program will prompt you for a ticker/CIK to find filings for.
For example, enter: 
0001166559

Scraper was tested on the following tickers:
Gates Foundation '0001166559'
Hershey Trust '0000908551'
Menlo Advisors '0001279708'
BlackRock '0001086364'
"""

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