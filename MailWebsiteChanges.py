#!/usr/bin/python

from BeautifulSoup import BeautifulSoup as Soup
from soupselect import select
import urllib
import re
import smtplib
from email.mime.text import MIMEText
import os.path
import sys
import time
from time import strftime
from xml.dom.minidom import parse, parseString

import config

separator = '\n\n'
emptyfeed = '<rss version="2.0"><channel><title>MailWebsiteChanges Feed</title><link>https://github.com/Debianguru/MailWebsiteChanges</link><description>The MailWebsiteChanges Feed</description></channel></rss>'


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


def sendmail(subject, content, sendAsHtml):
	if sendAsHtml:
		mail = MIMEText('<html><head><title>' + subject + '</title></head><body>' + content + '</body></html>', 'html')
	else:
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

	if config.rssfile != '':
		if os.path.isfile(config.rssfile):
			feedXML = parse(config.rssfile)
		else:
			feedXML = parseString(emptyfeed)


	for site in config.sites:

		fileContent = None

		if os.path.isfile(site[0] + '.txt'):
			file = open(site[0] + '.txt', 'r')
			fileContent = file.read()
			file.close()

		result = parseSite(site[1], site[2], site[3])
		content = result[0]
		isWarning = result[1]

		if isWarning == 1:
			subject = '[' + site[0] + '] WARNING'
			print 'WARNING: ' + content
			if config.receiver != '':
				sendmail(subject, content)
		elif content != fileContent:
			print site[0] + ' has been updated.'

			file = open(site[0] + '.txt', 'w')
			file.write(content)
			file.close()

                        if fileContent:
				subject = '[' + site[0] + '] ' + config.subjectPostfix
				if config.receiver != '':
					sendAsHtml = False if site[2] == '' else True
					sendmail(subject, content, sendAsHtml)

				if config.rssfile != '':
					feeditem = feedXML.createElement('item')
					titleitem = feedXML.createElement('title')
					titleitem.appendChild(feedXML.createTextNode(subject))
					feeditem.appendChild(titleitem)
					linkitem = feedXML.createElement('link')
					linkitem.appendChild(feedXML.createTextNode(site[1]))
					feeditem.appendChild(linkitem)
					descriptionitem = feedXML.createElement('description')
					descriptionitem.appendChild(feedXML.createTextNode(subject))
					feeditem.appendChild(descriptionitem)
					dateitem = feedXML.createElement('pubDate')
					dateitem.appendChild(feedXML.createTextNode(strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime())))
					feeditem.appendChild(dateitem)

					feedXML.getElementsByTagName('channel')[0].appendChild(feeditem)

	if config.rssfile != '':
		file = open(config.rssfile, 'w')
		file.write(feedXML.toxml())
		file.close()


if __name__ == "__main__":
	try:
		pollWebsites()
	except:
		msg = separator.join(map(str,sys.exc_info()))
		print msg
		if config.receiver != '':
			sendmail('[MailWebsiteChanges] Something went wrong ...', msg, 0)

