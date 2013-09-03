#!/usr/bin/python

from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select
import urllib
import re
import smtplib
from email.mime.text import MIMEText
import os.path
import sys
import config


separator = '\n\n'


def parseSite(uri, css, regex):
	isWarning = 0

	try:
		file = urllib.urlopen(uri)
	except IOError as e:
		return 'WARNING: could not open URL; maybe content was moved?\n\n' + str(e), 1

	if css == '':
		content = file.read()
	else:
		soup = Soup(file)

		result = select(soup, css)
		if len(result) == 0:
			content = "WARNING: selector became invalid!"
			isWarning = 1
		else:
			content = separator.join(map(str, result))

	if regex != '':
		result = re.findall(r'' + regex, content)
		if result == None:
			content = "WARNING: regex became invalid!"
			isWarning = 1
		else:
			content = separator.join(result)

	file.close()
	return content, isWarning


def sendmail(subject, content):
	mail = MIMEText(content)
	mail['From'] = config.sender
	mail['To'] = config.receiver
	mail['Subject'] = subject

	s = smtplib.SMTP(config.smtptlshost, config.smtptlsport)
	s.ehlo()
	s.starttls()
	s.login(config.smtptlsusername, config.smtptlspwd)
	s.sendmail(config.sender, config.receiver, mail.as_string())
	s.quit()


def pollWebsites():
	for site in config.sites:

		fileContent = ''
		firstTime = 1

		if os.path.isfile(site[0] + '.txt'):
			file = open(site[0] + '.txt', 'r')
			fileContent = file.read()
			file.close()
			firstTime = 0

		result = parseSite(site[1], site[2], site[3])
		content = result[0]
		isWarning = result[1]

		if isWarning == 1:
			subject = '[' + site[0] + '] WARNING'
			sendmail(subject, content)
		elif content != fileContent:
			print site[0] + ' has been updated.'

			file = open(site[0] + '.txt', 'w')
			file.write(content)
			file.close()

			if firstTime == 0:
				subject = '[' + site[0] + '] ' + config.subjectPostfix
				sendmail(subject, content)


if __name__ == "__main__":
	try:
		pollWebsites()
	except:
		sendmail('[MailWebsiteChanges] Something went wrong ...', '\n'.join(map(str,sys.exc_info())))

