from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select
import urllib
import re


def parseSite(site):
	if site[2] == '':
		file = urllib.urlopen(site[1])
		content = file.read()
		file.close()
	else:
		soup = Soup(urllib.urlopen(site[1]))

		result = select(soup, site[2])
		if len(result) == 0:
			content = "WARNING: selector became invalid!"
		else:
			content = ''
			for r in result:
				content += str(r) + '\n\n';

	if site[3] != '':
		result = re.findall(r'' + site[3], content)
		if result == None:
			content = "WARNING: regex became invalid!"
		else:
			content = '\n\n'.join(result)

	return content

