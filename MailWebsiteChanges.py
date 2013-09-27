#!/usr/bin/python

import urllib2
import urlparse
from lxml import etree
import re
import StringIO

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from urlparse import urljoin

import os
import traceback

import time
from time import strftime
import random

import config

defaultEncoding = 'utf-8'
emptyfeed = u'<rss version="2.0"><channel><title>MailWebsiteChanges Feed</title><link>https://github.com/Debianguru/MailWebsiteChanges</link><description>The MailWebsiteChanges Feed</description></channel></rss>'
uriAttributes = [['//img[@src]', 'src'], ['//a[@href]', 'href']]


def toAbsoluteURIs(trees, baseuri):
        for tree in trees:
                for uriAttribute in uriAttributes:
                        tags = tree.xpath(uriAttribute[0])
                        for tag in tags:
                                if urlparse.urlparse(tag.attrib[uriAttribute[1]]).scheme == '':
                                        tag.attrib[uriAttribute[1]] = urlparse.urljoin(baseuri, tag.attrib[uriAttribute[1]])


def parseSite(uri, contenttype, xpathquery, regex, enc):
        content, warning = None, None

        try:
                if xpathquery == '':
                        file = urllib2.urlopen(uri)
                        content = [file.read().decode(enc).encode(defaultEncoding)]
                        file.close()
                else:
                        baseuri = uri
                        if contenttype == 'html':
                                parser = etree.HTMLParser(encoding=enc)
                        else:
                                parser = etree.XMLParser(recover=True, encoding=enc)

                        file = urllib2.urlopen(uri)
                        tree = etree.parse(file, parser)
                        file.close()
                        result = tree.xpath(xpathquery)

                        if contenttype == 'html' and len(tree.xpath('/html/head/base')) != 0:
                                baseuri = tree.xpath('/html/head/base')[0].attrib['href']
                        toAbsoluteURIs(result, baseuri)

                        if len(result) == 0:
                                warning = "WARNING: selector became invalid!"
                        else:
                                content = [etree.tostring(s).decode(enc).encode(defaultEncoding) for s in result]
        except IOError as e:
                warning = 'WARNING: could not open URL; maybe content was moved?\n\n' + str(e)
                return {'content': content, 'warning': warning}

        if regex != '':
                newcontent = []
                for c in content:
                        newcontent.extend(re.findall(r'' + regex, c))
                content = newcontent
                if len(content) == 0:
                        warning = "WARNING: regex became invalid!"

        return {'content': content, 'warning': warning}


def genFeedItem(subject, content, link, change):
        feeditem = etree.Element('item')
        titleitem = etree.Element('title')
        titleitem.text = subject + ' #' + str(change)
        feeditem.append(titleitem)
        linkitem = etree.Element('link')
        linkitem.text = link
        feeditem.append(linkitem)
        descriptionitem = etree.Element('description')
        descriptionitem.text = content
        feeditem.append(descriptionitem)
        guiditem = etree.Element('guid')
        guiditem.text = str(random.getrandbits(32)) # subject + ' - ' + strftime("%b %d %Y %H:%M:%S", time.localtime()) + ' #' + str(change)
        feeditem.append(guiditem)
        dateitem = etree.Element('pubDate')
        dateitem.text = strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime())
        feeditem.append(dateitem)

        return feeditem


def sendmail(subject, content, sendAsHtml, link):
        if sendAsHtml:
                baseurl = None
                if link != None:
                        content = u'<p><a href="' + link + '">' + subject + u'</a></p>\n' + content
                        baseurl = urljoin(link, '/')
                mail = MIMEText('<html><head><title>' + subject + '</title>' + ('<base href="' + baseurl + '">' if baseurl else '') + '</head><body>' + content + '</body></html>', 'html', defaultEncoding)
        else:
                if link != None:
                        content = link + u'\n\n' + content
                mail = MIMEText(content, 'text', defaultEncoding)

        mail['From'] = config.sender
        mail['To'] = config.receiver
        mail['Subject'] = Header(subject, defaultEncoding)

        s = smtplib.SMTP(config.smtphost, config.smtpport)
        if config.useTLS:
                s.ehlo()
                s.starttls()
        s.login(config.smtpusername, config.smtppwd)
        s.sendmail(config.sender, config.receiver, mail.as_string())
        s.quit()


def getFileContents(shortname):
        result = []
        for f in os.listdir('.'):
                if f.startswith(shortname + '.') and f.endswith('.txt'):
                        file = open(f, 'r')
                        result.append(file.read())
                        file.close()
        return result


def storeFileContents(shortname, parseResult):
        for f in os.listdir('.'):
                if f.startswith(shortname + '.') and f.endswith('.txt'):
                        os.remove(f)

        i = 0
        for c in parseResult['content']:
                file = open(shortname + '.' + str(i) + '.txt', 'w')
                file.write(c)
                file.close()
                i += 1


def pollWebsites():

        if config.rssfile != '':
                if os.path.isfile(config.rssfile):
                        feedXML = etree.parse(config.rssfile)
                else:
                        feedXML = etree.parse(StringIO.StringIO(emptyfeed))

        for site in config.sites:

                print 'polling site [' + site['shortname'] + '] ...'
                parseResult = parseSite(site['uri'], site.get('type', 'html'), site.get('xpath', ''), site.get('regex', ''), site.get('encoding', defaultEncoding))

                if parseResult['warning']:
                        subject = '[' + site['shortname'] + '] WARNING'
                        print 'WARNING: ' + parseResult['warning']
                        if config.receiver != '':
                                sendmail(subject, parseResult['warning'], False, None)
                else:
                        changes = 0
                        fileContents = getFileContents(site['shortname'])
                        for content in parseResult['content']:
                                if content not in fileContents:
                                        changes += 1

                                        subject = '[' + site['shortname'] + '] ' + config.subjectPostfix
                                        if config.receiver != '':
                                                sendmail(subject, content, (site.get('xpath', '') != ''), site['uri'])

                                        if config.rssfile != '':
                                                feedXML.xpath('//channel')[0].append(genFeedItem(subject, content, site['uri'], changes))


                        if changes > 0:
                                storeFileContents(site['shortname'], parseResult)
                                print '        ' + str(changes) + ' updates'
 

        if config.rssfile != '':
                for o in feedXML.xpath('//channel/item[position()<last()-' + str(config.maxFeeds - 1) + ']'):
                        o.getparent().remove(o)
                file = open(config.rssfile, 'w')
                file.write(etree.tostring(feedXML))
                file.close()


if __name__ == "__main__":
        try:
                pollWebsites()
        except:
                msg = traceback.format_exc()
                print msg
                if config.receiver != '':
                        sendmail('[MailWebsiteChanges] Something went wrong ...', msg, False, None)

