#!/usr/bin/env python3

"""
main.py allows you to start the scraper. 

This program uses Python3, Selenium, PhantomJS,
and BeautifulSoup.

Before using the scraper:
1. Check that you have Python 3:
command: python3 --version
2. Create a virtual environment in Python
command: python3 -m venv myvenv
3. Activate virtual environment
command: source myvenv/bin/activate
4. Install requirements.txt
command: pip install -r requirements.txt
5. Install PhantomJS (if not already installed)

Scraper was tested on the following tickers:
Hershey Trust '0000908551'
Menlo Advisors '0001279708'
BlackRock '0001086364'
Gates Foundation '0001166559'
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