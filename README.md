# EDGAR 13F Scraper

## Installation
This program uses Python 3, Selenium, PhantomJS, 
BeautifulSoup, and lmxl.

Before using the scraper:
1. Check that you have Python 3:
    python3 --version
2. Navigate to project folder
3. Create a virtual environment in Python:
    python3 -m venv myvenv
4. Activate virtual environment:
    source myvenv/bin/activate
5. Install requirements.txt:
    pip install -r requirements.txt
6. Install PhantomJS (if not already installed)

## Files and Functionality
The EDGAR 13F Scraper parses fund holdings pulled from EDGAR, given a ticker or CIK. 

* main.py allows you to start the scraper. 
* scraper.py contains the main functionality to find and scrape holdings data from 13F filings on https://www.sec.gov.

To start scraper, run this command in an activated virtual environment:
python main.py

Program will prompt you for a ticker/CIK to find filings for.
Example format: 
0001166559

Note, the scraper will find all filings for a ticker and generate a text file for each filing in the same directory of the script. To avoid a large amount of generated files, you can get the most recent filing if you:
* comment out lines 78-86 and uncomment lines 88-89 in scraper.py

Scraper was tested on the following tickers:
* Gates Foundation '0001166559'
* Hershey Trust '0000908551'
* Menlo Advisors '0001279708'
* BlackRock '0001086364'
* Fidelity Advisors 'FELIX'

## Implementation for different 13F file formats
In 2013, the SEC discontinued ASCII text-based filing format and required the use of XML format.

The scraper handles both XML and ASCII text files in the following manner:
* First attempt to find the xml file on the documents page. 
If it exists, holdings retrieval for filings is done via parsing of 
XML from .xml link. Data is written to tab-delimited file.

* If xml file is not found, holdings retrieval for filings is done via parsing of 
.txt link. Scraper looks for table of holdings and saves it to a
temporary file. Temporary file is read and parsed again to
split each line by whitespace, allowing for writing tab-delimited text file.

