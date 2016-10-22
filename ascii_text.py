import urllib.request
import xml.etree.ElementTree as ET
import re
import csv
from astropy.io import ascii

url = 'https://www.sec.gov/Archives/edgar/data/908551/000090855109000003/0000908551-09-000003.txt'
#url = 'https://www.sec.gov/Archives/edgar/data/1166559/000104746911000932/0001047469-11-000932.txt'
#url = 'https://www.sec.gov/Archives/edgar/data/1279708/000127970813000005/0001279708-13-000005.txt'
# data = urllib.request.urlopen(url)
# parse = False
# holdings = []
# with open('holdingsFromXML.txt', 'w', newline='') as f:
# 	writer = csv.writer(f)
# 	for line in data:
# 		line = line.decode('UTF-8').strip()
# 		if re.search('^<TABLE>', line) or re.search('^<Table>', line):
# 			parse = True
# 		if re.search('^</TABLE>$', line) or re.search('^</Table>$', line):
# 			parse = False
# 		if parse:
# 			writer.writerow([line])

fh = open('holdingsFromXML.txt', 'r')
#data = fh.read()
#print(data)
holdings = []
# table = ascii.read(data, format='fixed_width', header_start=6, data_start=10)
# print(table)

# Pure Python
for line in fh:
	line = line.strip()
	columns = re.split(r'\s{2,}', line)
	# print(line)
	#print(columns)
	holdings.append(columns)
fh.close()
print(holdings)

with open('parsedHoldings.txt', 'w', newline='') as f:
    writer = csv.writer(f, dialect='excel-tab')
    # writer.writerow(['Ticker: ' + self.ticker])
    # writer.writerow(['Filing Date: ' + str(date)])
    # writer.writerow(['Period of Report: ' + str(period)])
    for row in holdings:
    	writer.writerow([row[i] for i in range(len(row))])

