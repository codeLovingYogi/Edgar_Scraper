#!/usr/bin/env python3
import csv
import datetime
import re
import sys
import time
import urllib.parse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SEC_LINK = "https://www.sec.gov/edgar/searchedgar/companysearch.html"


class HoldingsScraper:
    """Find holdings data in funds by scraping data from the SEC."""
    
    def __init__(self, ticker):
        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(1024, 768)
        self.ticker = ticker

    def find_filings(self):
        """Open SEC page, feed HTML into BeautifulSoup, and find filings."""
        self.browser.get(SEC_LINK)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        # enter query for filings
        search = self.browser.find_element_by_name('CIK')       
        search.send_keys(self.ticker)
        search.send_keys(Keys.RETURN)
        # wait for page to load search results
        wait = WebDriverWait(self.browser, 20)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tableFile2")))
        # filter search results by '13F' filings
        search = self.browser.find_element_by_name('type')
        filing_type = '13F'
        search.send_keys(filing_type)
        search.send_keys(Keys.RETURN)
        time.sleep(5)
        self.retrieve_filings()
    
    def retrieve_filings(self):
        """Retrieve filings for each 13F filing from search results."""
        sys.stdout.write('Retrieving filings...\n')
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        links = soup('a', id='documentsbutton')
        sys.stdout.write('13F filings found: %d\n' % len(links))
        # open each filing link
        # for link in links:
        #     url = link.get('href', None)
        #     print(url)
        # add domain for target filing link
        domain = 'https://www.sec.gov'
        url = domain + links[0].get('href', None)
        self.parse_filing(url)

    def parse_filing(self, url):
        """Open filing url, find and parse xml holdings data."""
        self.browser.get(url)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        xml_link = soup.find_all('a', text=re.compile("\informationtable.xml$"))
        #xml_file = 'https://www.sec.gov' + xml_link[0].get('href', None)
        xml_file = 'https://www.sec.gov/Archives/edgar/data/1166559/000110465916139781/a16-16809_1informationtable.xml'
        self.browser.get(xml_file)
        soup = BeautifulSoup(self.browser.page_source, "xml")
        self.browser.save_screenshot('search_results.png')
        holdings = soup.find_all('infoTable')
        data = []
        for i in range(len(holdings)):
            d = {}
            d['nameOfIssuer'] = holdings[i].find('nameOfIssuer').text
            d['titleOfClass'] = holdings[i].find('titleOfClass').text
            d['cusip'] = holdings[i].find('cusip').text
            d['value'] = holdings[i].find('value').text
            data.append(d)
        col_headers = list(d.keys())
        self.save_holdings(col_headers, data)
    
    def save_holdings(self, headers, data):
        """Write holdings data to tab-delimited file."""
        with open('myholdings.txt', 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel-tab')
            writer.writerow(headers)
            for row in data:
                writer.writerow([row.get(k, 'n/a') for k in headers])
        sys.stdout.write('Scraping complete, holdings data saved\n') 

    def scrape(self):
        """Main method to start scraper and find SEC holdings data."""
        results = self.find_filings()
        self.browser.quit()

#ticker = input('Enter ticker: ')
ticker = '0001166559'
while len(ticker) < 1:
    ticker = input('Please enter a ticker: ')
print(ticker)
sys.stdout.write('Scraping started at %s\n' % str(datetime.datetime.now()))
holdings = HoldingsScraper(ticker)
holdings.scrape()