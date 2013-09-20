#!/usr/bin/python

import urllib
from lxml import etree
from xml.sax.saxutils import escape
import re
import StringIO

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import os.path
import sys

import time
from time import strftime


import config

separator = '\n\n'
defaultEncoding = 'utf-8'
emptyfeed = '<rss version="2.0"><channel><title>MailWebsiteChanges Feed</title><link>https://github.com/Debianguru/MailWebsiteChanges</link><description>The MailWebsiteChanges Feed</description></channel></rss>'


def parseSite(uri, contenttype, xpathquery, regex, enc):
        content, warning = None, None

        try:
                if xpathquery == '':
                        file = urllib.urlopen(uri)
                        content = file.read()
                        file.close()
                else:
                        if contenttype == 'xml':
                                parser = etree.XMLParser(recover=True, encoding=enc)
                        else:
                                parser = etree.HTMLParser(encoding=enc)

                        tree = etree.parse(uri, parser)
                        result = tree.xpath(xpathquery)

                        if len(result) == 0:
                                warning = "WARNING: selector became invalid!"
                        else:
                                content = separator.join([etree.tostring(s, encoding=enc) for s in result])
        except IOError as e:
                warning = 'WARNING: could not open URL; maybe content was moved?\n\n' + str(e)
                return content, warning

        if regex != '':
                result = re.findall(r'' + regex, content)
                if result == None:
                        warning = "WARNING: regex became invalid!"
                else:
                        content = separator.join(result)

        return content, warning


def sendmail(subject, content, sendAsHtml, encoding, link):
        if sendAsHtml:
                if link != None:
                        content = '<p><a href="' + link + '">' + subject + '</a></p>\n' + content
                mail = MIMEText('<html><head><title>' + subject + '</title></head><body>' + content + '</body></html>', 'html', encoding)
        else:
                if link != None:
                        content = link + '\n\n' + content
                mail = MIMEText(content, 'text', encoding)

        mail['From'] = config.sender
        mail['To'] = config.receiver
        mail['Subject'] = Header(subject, encoding)

        s = smtplib.SMTP(config.smtptlshost, config.smtptlsport)
        s.ehlo()
        s.starttls()
        s.login(config.smtptlsusername, config.smtptlspwd)
        s.sendmail(config.sender, config.receiver, mail.as_string())
        s.quit()


def pollWebsites():

        if config.rssfile != '':
                if os.path.isfile(config.rssfile):
                        feedXML = etree.parse(config.rssfile)
                else:
                        feedXML = etree.parse(StringIO.StringIO(emptyfeed))

        for site in config.sites:

                fileContent = None

                if os.path.isfile(site['shortname'] + '.txt'):
                        file = open(site['shortname'] + '.txt', 'r')
                        fileContent = file.read()
                        file.close()

		print 'polling site [' + site['shortname'] + '] ...'
                content, warning = parseSite(site['uri'], site['type'], site['xpath'], site['regex'], site['encoding'])

                if warning:
                        subject = '[' + site['shortname'] + '] WARNING'
                        print 'WARNING: ' + warning
                        if config.receiver != '':
                                sendmail(subject, warning, False, defaultEncoding, None)
                elif content != fileContent:
                        print '[' + site['shortname'] + '] has been updated.'

                        file = open(site['shortname'] + '.txt', 'w')
                        file.write(content)
                        file.close()

                        if fileContent:
                                subject = '[' + site['shortname'] + '] ' + config.subjectPostfix
                                if config.receiver != '':
                                        sendmail(subject, content, (site['xpath'] != ''), site['encoding'], site['uri'])

                                if config.rssfile != '':
                                        feeditem = etree.Element('item')
                                        titleitem = etree.Element('title')
                                        titleitem.text = subject
                                        feeditem.append(titleitem)
                                        linkitem = etree.Element('link')
                                        linkitem.text = site['uri']
                                        feeditem.append(linkitem)
                                        descriptionitem = etree.Element('description')
                                        print escape(content)
                                        descriptionitem.text = subject  #escape(content)

                                        feeditem.append(descriptionitem)
                                        dateitem = etree.Element('pubDate')
                                        dateitem.text = strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime())
                                        feeditem.append(dateitem)

                                        feedXML.xpath('//channel')[0].append(feeditem)

        if config.rssfile != '':
                file = open(config.rssfile, 'w')
                file.write(etree.tostring(feedXML))
                file.close()


if __name__ == "__main__":
        try:
                pollWebsites()
        except:
                msg = separator.join(map(str,sys.exc_info()))
                print msg
                if config.receiver != '':
                        sendmail('[MailWebsiteChanges] Something went wrong ...', msg, False, defaultEncoding, None)

