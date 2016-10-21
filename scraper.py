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
        try:
            wait = WebDriverWait(self.browser, 20)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tableFile2")))
            # filter search results by '13F' filings
            search = self.browser.find_element_by_name('type')
            filing_type = '13F'
            search.send_keys(filing_type)
            search.send_keys(Keys.RETURN)
            time.sleep(5)
            self.retrieve_filings()
        except:
            sys.stdout.write('No results found for ticker: %s\n' % self.ticker)
    
    def retrieve_filings(self):
        """Retrieve filings for each 13F filing from search results."""
        sys.stdout.write('Retrieving filings for: %s\n' % self.ticker)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        links = soup('a', id='documentsbutton')
        sys.stdout.write('13F filings found: %d\n' % len(links))
        domain = 'https://www.sec.gov'
        # Loop through all filings found
        for link in links:
            url = domain + link.get('href', None)
            self.parse_filing(url)
        # Below is for most recent filing only
        # url = domain + links[0].get('href', None)
        # self.parse_filing(url)

    def parse_filing(self, url):
        """Open filing url, find xml holdings data."""
        self.browser.get(url)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        filing_date_loc = soup.find("div", text="Filing Date")
        filing_date = filing_date_loc.findNext('div').text
        period_of_report_loc = soup.find("div", text="Period of Report")
        period_of_report = period_of_report_loc.findNext('div').text
        #sys.stdout.write('Getting data for: %s\n' % str(period_of_report))
        try:
            xml_link = soup.find('td', text="2").findNext('a', text=re.compile("\.xml$"))
            xml_file = 'https://www.sec.gov' + xml_link.get('href', None)
            sys.stdout.write('Getting holdings from: %s\n' % xml_file)
            self.get_holdings(xml_file, filing_date, period_of_report)
        except:
            sys.stdout.write('No xml link found for filing date: %s\n' % str(filing_date))

    def get_holdings(self, xml_file, date, period):
        """Get detail for each holding from xml file."""
        self.browser.get(xml_file)
        soup = BeautifulSoup(self.browser.page_source, "xml")
        holdings = soup.find_all('infoTable')
        data = []
        for i in range(len(holdings)):
            d = {}
            d['nameOfIssuer'] = holdings[i].find('nameOfIssuer').text
            d['titleOfClass'] = holdings[i].find('titleOfClass').text
            d['cusip'] = holdings[i].find('cusip').text
            d['value'] = holdings[i].find('value').text
            d['sshPrnamt'] = holdings[i].find('shrsOrPrnAmt').find('sshPrnamt').text
            d['sshPrnamtType'] = holdings[i].find('shrsOrPrnAmt').find('sshPrnamtType').text
            d['investmentDiscretion'] = holdings[i].find('investmentDiscretion').text
            d['votingAuthoritySole'] = holdings[i].find('votingAuthority').find('Sole').text
            d['votingAuthorityShared'] = holdings[i].find('votingAuthority').find('Shared').text
            d['votingAuthorityNone'] = holdings[i].find('votingAuthority').find('None').text
            data.append(d)
        col_headers = list(d.keys())
        self.save_holdings(date, period, col_headers, data)
    
    def save_holdings(self, date, period, headers, data):
        """Create and write holdings data to tab-delimited text file."""
        file_name = self.ticker + '_' + str(date) + '_filing_date.txt'
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel-tab')
            writer.writerow(['Ticker: ' + self.ticker])
            writer.writerow(['Filing Date: ' + str(date)])
            writer.writerow(['Period of Report: ' + str(period)])
            writer.writerow(headers)
            for row in data:
                writer.writerow([row.get(k, 'n/a') for k in headers])
        sys.stdout.write('Scraping complete, holdings data saved\n') 

    def scrape(self):
        """Main method to start scraper and find SEC holdings data."""
        self.find_filings()
        self.browser.quit()
