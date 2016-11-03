#!/usr/bin/env python3

"""
scraper.py contains the main functionality to find and scrape
holdings data from 13F filings on https://www.sec.gov.

See comments in README.md for instructions on how to run
the scraper. 

Note, the scraper will find all filings for a ticker and 
generated a text file for each in the current directory. 
To test on the most recent filing only, you can comment out 
lines 78-86, and uncomment lines 88-89 in scraper.py
"""

import csv
import datetime
import os
import re
import sys
import time
import urllib.request
import urllib.parse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

SEC_LINK = "https://www.sec.gov/edgar/searchedgar/companysearch.html"
DOMAIN = "https://www.sec.gov"


class HoldingsScraper:
    """Find holdings data in funds by scraping data from the SEC."""
    
    def __init__(self, ticker):
        self.browser = webdriver.PhantomJS()
        self.browser.set_window_size(1024, 768)
        self.ticker = ticker
        self.links = []

    def find_filings(self):
        """Open SEC page, feed HTML into BeautifulSoup, and find filings."""
        self.browser.get(SEC_LINK)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        
        # Enter ticker to query filings
        search = self.browser.find_element_by_name('CIK')       
        search.send_keys(self.ticker)
        search.send_keys(Keys.RETURN)

        try:
            wait = WebDriverWait(self.browser, 20)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".tableFile2")))
            
            # Filter search results by '13F' filings
            search = self.browser.find_element_by_name('type')
            filing_type = '13F'
            search.send_keys(filing_type)
            search.send_keys(Keys.RETURN)
            time.sleep(5)
            self.retrieve_filings()
        except:
            sys.stdout.write('No results found for ticker: %s\n' % self.ticker)
    
    def retrieve_filings(self):
        """Retrieve links for all 13F filing from search results."""
        sys.stdout.write('Retrieving filings for: %s\n' % self.ticker)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        self.links.extend(soup('a', id='documentsbutton'))
        sys.stdout.write('13F filings found: %d\n' % len(self.links))
        
        # Comment out try/except lines below to run most recent filing only
        # Checks for more results and click next page
        try:
            next = self.browser.find_element_by_xpath("//input[@value='Next 40']")
            next.click()
            self.retrieve_filings()
        except:
            # Otherwise loop through all filings found to get data
            for link in self.links:
                url = DOMAIN + link.get('href', None)
                self.parse_filing(url)
        # Uncomment below to run most recent filing only
        # url = DOMAIN + self.links[0].get('href', None)
        # self.parse_filing(url)

    def parse_filing(self, url):
        """Examines filing to determine how to parse holdings data.
        
        Opens filing url, get filing and report end dates, and determine 
        parsing by either XML or ASCII based on 2013 filing format change.
        """
        self.browser.get(url)
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        
        # Find report information for text file headers
        filing_date_loc = soup.find("div", text="Filing Date")
        filing_date = filing_date_loc.findNext('div').text
        period_of_report_loc = soup.find("div", text="Period of Report")
        period_of_report = period_of_report_loc.findNext('div').text

        # Prepare report header and file_name for each text file
        report_detail = self.report_info(filing_date, period_of_report)
        file_name = report_detail[0]
        report_headers = report_detail[1]
        
        # Determine if xml file exists, if not look for ASCII text file
        try:
            xml = soup.find('td', text="2")
            xml_link = xml.findNext('a', text=re.compile("\.xml$"))
            xml_file = DOMAIN + xml_link.get('href', None)
            sys.stdout.write('Getting holdings from: %s\n' % xml_file)
            holdings = self.get_holdings_xml(xml_file)
            col_headers = holdings[0]
            data = holdings[1]
            self.save_holdings_xml(file_name, report_headers, col_headers, data)

        except:
            ascii = soup.find('td', text="Complete submission text file")
            ascii_link = ascii.findNext('a', text=re.compile("\.txt$"))
            txt_file = DOMAIN + ascii_link.get('href', None)
            sys.stdout.write('Getting holdings from (ascii): %s\n' % txt_file)
            holdings = self.get_holdings_ascii(txt_file)
            self.save_holdings_ascii(file_name, report_headers, holdings)

    def report_info(self, date, period):
        """Prep report headers to be written to text file. """
        file_name = self.ticker + '_' + str(date) + '_filing_date.txt'
        headers = []
        headers.append('Ticker: ' + self.ticker)
        headers.append('Filing Date: ' + str(date))
        headers.append('Period of Report: ' + str(period))
        return(file_name, headers)

    def get_holdings_xml(self, xml_file):
        """Get holdings detail from xml file and store data.

        XML format for filings was required by SEC in 2013.
        """
        self.browser.get(xml_file)
        soup = BeautifulSoup(self.browser.page_source, "xml")
        holdings = soup.find_all('infoTable')
        data = []
        # Attempt retrieval of available attributes for 13F filings
        for i in range(len(holdings)):
            d = {}
            try:
                d['nameOfIssuer'] = holdings[i].find('nameOfIssuer').text
            except:
                pass
            try:
                d['titleOfClass'] = holdings[i].find('titleOfClass').text
            except:
                pass
            try:
                d['cusip'] = holdings[i].find('cusip').text
            except:
                pass
            try:
                d['value'] = holdings[i].find('value').text
            except:
                pass
            try:
                d['sshPrnamt'] = holdings[i].find('shrsOrPrnAmt').find('sshPrnamt').text
            except:
                pass
            try:
                d['sshPrnamtType'] = holdings[i].find('shrsOrPrnAmt').find('sshPrnamtType').text
            except:
                pass
            try:
                d['putCall'] = holdings[i].find('putCall').text
            except:
                 pass
            try:
                d['investmentDiscretion'] = holdings[i].find('investmentDiscretion').text
            except:
                pass
            try:
                d['otherManager'] = holdings[i].find('otherManager').text
            except:
                pass
            try:
                d['votingAuthoritySole'] = holdings[i].find('votingAuthority').find('Sole').text
            except:
                pass
            try:
                d['votingAuthorityShared'] = holdings[i].find('votingAuthority').find('Shared').text
            except:
                pass
            try:
                d['votingAuthorityNone'] = holdings[i].find('votingAuthority').find('None').text
            except:
                pass
            data.append(d)
        
        col_headers = list(d.keys())
        return(col_headers, data)

    def save_holdings_xml(self, file_name, report_headers, col_headers, data):
        """Create and write holdings data from XML to tab-delimited text file."""
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f, dialect='excel-tab')
            for i in range(len(report_headers)):
                writer.writerow([report_headers[i]])
            writer.writerow(col_headers)
            for row in data:
                writer.writerow([row.get(k, 'n/a') for k in col_headers])

    def get_holdings_ascii(self, txt_file):
        """Get holdings detail from ASCII file and store data.

        ASCII format was used pre-2013 decision to use XML. Read and find
        holdings details from ASCII text file. Store data in 'temp_holdings.txt'
        file for save_holdings_ascii().
        """
        data = urllib.request.urlopen(txt_file)
        parse = False
        temp_file = 'temp_holdings.txt'
        with open(temp_file, 'w', newline='') as f:
            writer = csv.writer(f)
            # Look for table storing holdings data before writing to file
            for line in data:
                line = line.decode('UTF-8').strip()
                if re.search('^<TABLE>', line) or re.search('^<Table>', line):
                    parse = True
                if re.search('^</TABLE>$', line) or re.search('^</Table>$', line):
                    parse = False
                if parse:
                    writer.writerow([line])

        return(temp_file)

    def save_holdings_ascii(self, file_name, report_headers, data):
        """Retrieves and reads 'temp_holdings.txt', then writes to tab-delimited file.

        Parse holdings data in ASCII text format, splitting each line 
        by looking for 2 or more whitespaces, stores each line in 'holdings', 
        then writes to tab-delimited text file.
        """
        with open(data, 'r') as f:
            holdings = []
            for line in f:
                line = line.strip()
                columns = re.split(r'\s{2,}', line)
                holdings.append(columns)

        # Write tab delimited file
        file_name = 'ASCII_' + file_name
        with open(file_name, 'w', newline='') as f:     
            writer = csv.writer(f, dialect='excel-tab')
            for i in range(len(report_headers)):
                writer.writerow([report_headers[i]])
            for row in holdings:
                writer.writerow([row[i] for i in range(len(row))])

    def remove_temp_file(self):
        """Deletes temp file used to parse ASCII data."""
        os.remove('temp_holdings.txt')

    def scrape(self):
        """Main method to start scraper and find SEC holdings data."""
        self.find_filings()
        self.browser.quit()
