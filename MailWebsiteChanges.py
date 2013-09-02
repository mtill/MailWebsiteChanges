#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
import os.path
import func
import config


for site in config.sites:

	fileContent = ''
	firstTime = 1

	if os.path.isfile(site[0] + '.txt'):
		file = open(site[0] + '.txt', 'r')
		fileContent = file.read()
		file.close()
		firstTime = 0

	content = func.parseSite(site)

	if content != fileContent:
		print site[0] + ' has been updated.'

		file = open(site[0] + '.txt', 'w')
		file.write(content)
		file.close()

		if firstTime == 0:
			mail = MIMEText(content)
			mail['From'] = config.sender
			mail['To'] = config.receiver
			mail['Subject'] = '[' + site[0] + '] ' + config.subjectPostfix

			s = smtplib.SMTP(config.smtptlshost, config.smtptlsport)
			s.ehlo()
			s.starttls()
			s.login(config.smtptlsusername, config.smtptlspwd)
			s.sendmail(config.sender, config.receiver, mail.as_string())
			s.quit()

