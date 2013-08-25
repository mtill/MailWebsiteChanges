#!/usr/bin/python

from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select
import urllib
import os.path
import smtplib
from email.mime.text import MIMEText
import re

# some examples; use "html" to enable CSS selector mode or "text to use regular expressions
sites = [['shortname1', 'http://www.mywebsite1.com/info', 'html', 'h1'],
         ['shortname2', 'http://www.mywebsite2.com/info', 'html', '.theClass > h3'],
         ['shortname3', 'http://www.mywebsite3.com', 'text', 'Version\"\:\d*\.\d*']
        ]


#os.chdir('/path/to/working/directory')
subjectPostfix = 'A website has been updated!'
sender = 'me@mymail.com'
smtptlshost = 'mysmtpprovider.com'
smtptlsport = 587
smtptlsusername = sender
smtptlspwd = 'mypassword'
receiver = 'me2@mymail.com'



for site in sites:

	fileContent = ''
	firstTime = 1

	if os.path.isfile(site[0] + '.txt'):
		file = open(site[0] + '.txt', 'r')
		fileContent = file.read()
		file.close()
		firstTime = 0

	if site[2] == 'html':
		soup = Soup(urllib.urlopen(site[1]))
		result = select(soup, site[3])
		if len(result) == 0:
			content = "WARNING: selector became invalid!"
		else:
			content = str(result[0])

	elif site[2] == 'text':
		file = urllib.urlopen(site[1])
		result = re.findall(r'' + site[3], file.read())
		if result == None:
			content = "WARNING: regex became invalid!"
		else:
			content = '\n'.join(result)
		file.close()
	else:
		print 'Invalid content type!'
		exit(1)

	if content != fileContent:
		print site[0] + ' has been updated.'

		file = open(site[0] + '.txt', 'w')
		file.write(content)
		file.close()

		if firstTime == 0:
			mail = MIMEText(content)
			mail['From'] = sender
			mail['To'] = receiver
			mail['Subject'] = '[' + site[0] + '] ' + subjectPostfix

			s = smtplib.SMTP(smtptlshost, smtptlsport)
			s.ehlo()
			s.starttls()
			s.login(smtptlsusername, smtptlspwd)
			s.sendmail(sender, receiver, mail.as_string())
			s.quit()

