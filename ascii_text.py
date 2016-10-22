import urllib.request
import xml.etree.ElementTree as ET
import re
import csv

#url = 'https://www.sec.gov/Archives/edgar/data/908551/000090855109000003/0000908551-09-000003.txt'
url = 'https://www.sec.gov/Archives/edgar/data/1166559/000104746911000932/0001047469-11-000932.txt'
data = urllib.request.urlopen(url)
parse = False
holdings = []
with open('holdingsFromXML.txt', 'w', newline='') as f:
	writer = csv.writer(f)
	for line in data:
		line = line.decode('UTF-8').strip()
		if re.search('^<TABLE>$', line) or re.search('^<Table>$', line):
			parse = True
		if re.search('^</TABLE>$', line) or re.search('^</Table>$', line):
			parse = False
		if parse:
			writer.writerow([line])

# x = re.findall(r'<TABLE>(.*?)</TABLE>',data,re.DOTALL)
# # print(x)

# with open(file_name, 'w', newline='') as f:
#     writer = csv.writer(f, dialect='excel-tab')
#     writer.writerow(['Ticker: ' + self.ticker])
#     writer.writerow(['Filing Date: ' + str(date)])
#     writer.writerow(['Period of Report: ' + str(period)])
#     writer.writerow(headers)
#     for row in data:
#         writer.writerow([row.get(k, 'n/a') for k in headers])