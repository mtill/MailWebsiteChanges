#!/usr/bin/python

from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select
import urllib
import sys
import re


site = sys.argv   # invoke this script with e.g., "http://www.rockbox.org/download/" "html" "h1"

print site[1]

if site[2] == 'html':
	soup = Soup(urllib.urlopen(site[1]))
	result = select(soup, site[3])
	if len(result) == 0:
		content = "WARNING: selector became invalid!"
	else:
		content = str(result[0])
elif site[2] == 'text':
	file = urllib.urlopen(site[1])
	result = re.findall(site[3], file.read())
	if result == None:
		content = "WARNING: regex became invalid!"
	else:
		content = '\n'.join(result)
	file.close()
else:
	print 'Invalid content type!'
	exit(1)

print content

