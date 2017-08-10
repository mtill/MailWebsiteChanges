#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright: (2013-2015) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from lxml import etree
from cssselect import GenericTranslator
import re
import io
import hashlib

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from urllib.parse import urljoin

import os
import sys
import getopt
import traceback

import subprocess

import time
from time import strftime
import random

import importlib
config = None

defaultEncoding = 'utf-8'
maxTitleLength = 150

# this is how an empty RSS feed looks like
emptyfeed = """<?xml version="1.0"?>
<rss version="2.0">
 <channel>
  <title>MailWebsiteChanges Feed</title>
  <link>https://github.com/Debianguru/MailWebsiteChanges</link>
  <description>MailWebsiteChanges Feed</description>
 </channel>
</rss>"""

# Attributes in HTML files storing URI values. These values are automatically translated to absolute URIs.
uriAttributes = [['//img[@src]', 'src'], ['//a[@href]', 'href']]
cmdscheme = 'cmd://'

mailsession = None


# translates all relative URIs found in trees to absolute URIs
def toAbsoluteURIs(trees, baseuri):
    for tree in trees:
        if isinstance(tree, str):
            continue
        for uriAttribute in uriAttributes:
            tags = tree.xpath(uriAttribute[0])
            for tag in tags:
                if tag.attrib.get(uriAttribute[1]) != None:
                    if urllib.parse.urlparse(tag.attrib[uriAttribute[1]]).scheme == '':
                        tag.attrib[uriAttribute[1]] = urllib.parse.urljoin(baseuri, tag.attrib[uriAttribute[1]])


def parseSite(site):
    global defaultEncoding
    file, content, titles, warning = None, None, None, None

    uri = site['uri']
    contenttype = site.get('type', 'html')
    contentregex = site.get('contentregex', '')
    titleregex = site.get('titleregex', '')
    splitregex = site.get('splitregex', '')
    enc = site.get('encoding', defaultEncoding)

    contentxpath = site.get('contentxpath', '')
    if contentxpath == '' and site.get('contentcss', '') != '':
        # CSS
        contentxpath = GenericTranslator().css_to_xpath(site.get('contentcss'))
    titlexpath = site.get('titlexpath', '')
    if titlexpath == '' and site.get('titlecss', '') != '':
        titlexpath = GenericTranslator().css_to_xpath(site.get('titlecss'))

    try:

        if uri.startswith(cmdscheme):
            # run command and retrieve output
            process = subprocess.Popen(uri[len(cmdscheme):], stdout=subprocess.PIPE, shell=True, close_fds=True)
            file = process.stdout
        else:
            # open website
            req = urllib.request.Request(uri)
            if 'user-agent' in site:
                req.add_header('User-Agent', site['user-agent'])
            if 'accept' in site:
                req.add_header('Accept', site['accept'])
            file = urllib.request.urlopen(req)


        if contenttype == 'text' or (contentxpath == '' and titlexpath == ''):
            thefullcontent = file.read().decode(enc, errors='ignore')
            contents = [thefullcontent]
            if splitregex != '':
                contents = thefullcontent.split(splitregex)
            titles = []
        else:
            baseuri = uri
            if contenttype == 'html':
                parser = etree.HTMLParser(encoding=enc)
            else:
                parser = etree.XMLParser(recover=True, encoding=enc)

            tree = etree.parse(file, parser)

            # xpath
            contentresult = tree.xpath(contentxpath) if contentxpath else []
            titleresult = tree.xpath(titlexpath) if titlexpath else []

            # translate relative URIs to absolute URIs
            if contenttype == 'html':
                basetaglist = tree.xpath('/html/head/base')
                if len(basetaglist) != 0:
                    baseuri = basetaglist[0].attrib['href']
                if len(contentresult) != 0:
                    toAbsoluteURIs(contentresult, baseuri)
                if len(titleresult) != 0:
                    toAbsoluteURIs(titleresult, baseuri)

            if contentxpath != '' and titlexpath != '' and len(contentresult) != len(titleresult):
                warning = 'WARNING: number of title blocks (' + str(len(titleresult)) + ') does not match number of content blocks (' + str(len(contentresult)) + ')'
            elif contentxpath and len(contentresult) == 0:
                warning = 'WARNING: content selector became invalid!'
            elif titlexpath and len(titleresult) == 0:
                warning = 'WARNING: title selector became invalid!'
            else:
                if len(contentresult) == 0:
                    contentresult = titleresult
                if len(titleresult) == 0:
                    titleresult = contentresult

            if isinstance(contentresult, str):
                contents = [contentresult]
            else:
                contents = [etree.tostring(s, encoding=enc, pretty_print=True).decode(enc, errors='ignore') for s in contentresult]
            if isinstance(titleresult, str):
                titles = [getSubject(titleresult)]
            else:
                titles = [getSubject(etree.tostring(s, method='text', encoding=enc).decode(enc, errors='ignore')) for s in titleresult]

    except IOError as e:
        warning = 'WARNING: could not open URL; maybe content was moved?\n\n' + str(e)

    if file is not None:
        file.close()

    if uri.startswith(cmdscheme) and process.wait() != 0:
        warning = 'WARNING: process terminated with an error'

    if warning:
        return {'content': content, 'titles': titles, 'warning': warning}

    # parse regex
    if contentregex:
        contents = [x for y in [re.findall(r'' + contentregex, c, re.S) for c in contents] for x in y]
    if titleregex:
        titles = [x for y in [re.findall(r'' + titleregex, c, re.S) for c in titles] for x in y]

    if contentregex and titleregex and len(contents) != len(titles):
        warning = 'WARNING: number of title blocks (' + str(len(titles)) + ') does not match number of content blocks (' + str(len(contents)) + ') after regex'
    elif contentregex and len(contents) == 0:
        warning = 'WARNING: content regex became invalid!'
    elif titleregex and len(titles) == 0:
        warning = 'WARNING: title regex became invalid!'
    else:
        if len(contents) == 0:
            contents = titles
        if len(titles) == 0:
            titles = [getSubject(c) for c in contents]

    return {'contents': contents, 'titles': titles, 'warning': warning}


# returns a short subject line
def getSubject(textContent):
    if textContent == None or textContent == '':
        return config.subjectPostfix
    textContent = re.sub(' +', ' ', re.sub('\s', ' ', textContent)).strip()
    return (textContent[:maxTitleLength] + ' [..]') if len(textContent) > maxTitleLength else textContent


# generates a new RSS feed item
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
    guiditem.text = str(random.getrandbits(32))
    feeditem.append(guiditem)
    dateitem = etree.Element('pubDate')
    dateitem.text = strftime("%a, %d %b %Y %H:%M:%S %Z", time.localtime())
    feeditem.append(dateitem)

    return feeditem


# sends mail notification
def sendmail(receiver, subject, content, sendAsHtml, link):
    global mailsession, defaultEncoding

    if sendAsHtml:
        baseurl = None
        if link != None:
            content = '<p><a href="' + link + '">' + subject + '</a></p>\n' + content
            baseurl = urljoin(link, '/')
        mail = MIMEText('<html><head><title>' + subject + '</title>' + ('<base href="' + baseurl + '">' if baseurl else '') + '</head><body>' + content + '</body></html>', 'html', defaultEncoding)
    else:
        if link != None:
            content = link + '\n\n' + content
        mail = MIMEText(content, 'text', defaultEncoding)

    mail['From'] = config.sender
    mail['To'] = receiver
    mail['Subject'] = Header(subject, defaultEncoding)

    # initialize session once, not each time this method gets called
    if mailsession is None:
        mailsession = smtplib.SMTP(config.smtphost, config.smtpport)
        if config.useTLS:
            mailsession.ehlo()
            mailsession.starttls()
        if config.smtpusername is not None:
            mailsession.login(config.smtpusername, config.smtppwd)

    mailsession.sendmail(config.sender, receiver.split(','), mail.as_string())


# returns a list of all content that is stored locally for a specific site
def getStoredHashes(shortname):

    result = []
    filename = shortname + ".txt"
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file:
                result.append(line.rstrip())

    return result


# updates list of content that is stored locally for a specific site
def storeHashes(shortname, contentHashes):

    with open(shortname + '.txt', 'w') as file:
        for h in contentHashes:
            file.write(h + "\n")


def pollWebsites():
    global defaultEncoding

    # parse existing feed or create a new one
    if config.enableRSSFeed:
        if os.path.isfile(config.rssfile):
            feedXML = etree.parse(config.rssfile)
        else:
            feedXML = etree.parse(io.StringIO(emptyfeed))

    # start polling sites
    mailsSent = 0
    for site in config.sites:
        print('polling site [' + site['shortname'] + '] ...')
        sessionHashes = []
        parseResult = parseSite(site)
        receiver = site.get('receiver', config.receiver)

        # if something went wrong, notify the user
        if parseResult['warning']:
            subject = '[' + site['shortname'] + '] WARNING'
            print('WARNING: ' + parseResult['warning'])
            if config.enableMailNotifications:
                if config.maxMailsPerSession == -1 or mailsSent < config.maxMailsPerSession:
                    sendmail(receiver, subject, parseResult['warning'], False, None)
                    mailsSent = mailsSent + 1
            if config.enableRSSFeed:
                feedXML.xpath('//channel')[0].append(genFeedItem(subject, parseResult['warning'], site['uri'], 0))
        else:
            # otherwise, check which parts of the site were updated
            changes = 0
            fileHashes = getStoredHashes(site['shortname'])
            i = 0
            for content in parseResult['contents']:

                contenthash = hashlib.md5(content.encode(defaultEncoding)).hexdigest()
                if contenthash not in fileHashes:
                    if config.maxMailsPerSession == -1 or mailsSent < config.maxMailsPerSession:
                        changes += 1
                        sessionHashes.append(contenthash)

                        subject = '[' + site['shortname'] + '] ' + parseResult['titles'][i]
                        print('    ' + subject)
                        if config.enableMailNotifications and len(fileHashes) > 0:
                            sendmail(receiver, subject, content, (site.get('type', 'html') == 'html'), site['uri'])
                            mailsSent = mailsSent + 1

                        if config.enableRSSFeed:
                            feedXML.xpath('//channel')[0].append(genFeedItem(subject, content, site['uri'], changes))
                else:
                    sessionHashes.append(contenthash)

                i += 1


            if changes > 0:
                storeHashes(site['shortname'], sessionHashes)
                print('        ' + str(changes) + ' updates')

    # store feed
    if config.enableRSSFeed:
        for o in feedXML.xpath('//channel/item[position()<last()-' + str(config.maxFeeds - 1) + ']'):
            o.getparent().remove(o)
        file = open(config.rssfile, 'w')
        file.write(etree.tostring(feedXML, pretty_print=True, xml_declaration=True, encoding=defaultEncoding).decode(defaultEncoding, errors='ignore'))
        file.close()


if __name__ == "__main__":

    configMod = 'config'
    dryrun = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:d:', ['help', 'config=', 'dry-run='])
    except getopt.GetoptError:
        print('Usage: mwc.py --config=config --dry-run=shortname')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: mwc.py --config=config')
            exit()
        elif opt in ('-c', '--config'):
            configMod = arg
        elif opt in ('-d', '--dry-run'):
            dryrun = arg

    config = importlib.import_module(configMod)

    if dryrun:
        for site in config.sites:
            if site['shortname'] == dryrun:
                parseResult = parseSite(site)
                print(parseResult)
                print(str(len(parseResult['contents'])) + " results")
                break
    else:
        try:
            pollWebsites()
        except:
            msg = str(sys.exc_info()[0]) + '\n\n' + traceback.format_exc()
            print(msg)
            if config.receiver != '':
                sendmail(config.receiver, '[mwc] Something went wrong ...', msg, False, None)

        if mailsession:
            mailsession.quit()
            mailsession = None
