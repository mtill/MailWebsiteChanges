#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright: (2013-2017) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+


import urllib.request
import urllib.error
import urllib.parse
import subprocess

from lxml import etree
from cssselect import GenericTranslator
import re


# Attributes in HTML files storing URI values. These values are automatically translated to absolute URIs.
uriAttributes = [['//img[@src]', 'src'], ['//a[@href]', 'href']]

maxTitleLength = 150


class Parser:
    # input: [Content], output: [Content]
    def performAction(self, contentList):
        pass


class Receiver(Parser):
    def __init__(self, uri):
        self.uri = uri


class Content:
    def __init__(self, uri, encoding, title, content, contenttype, additional=None):
        self.uri = uri
        self.encoding = encoding
        self.title = title
        self.content = content
        self.contenttype = contenttype
        self.additional = additional


# returns a short subject line
def getSubject(textContent):
    global maxTitleLength
    
    if textContent is None or len(textContent.strip()) == 0:
        return 'Website has been updated'
    textContent = re.sub(' +', ' ', re.sub('\s', ' ', textContent)).strip()
    return (textContent[:maxTitleLength] + ' [..]') if len(textContent) > maxTitleLength else textContent


# translates all relative URIs found in trees to absolute URIs
def toAbsoluteURIs(trees, baseuri):
    global uriAttributes

    for tree in trees:
        if isinstance(tree, str):
            continue
        for uriAttribute in uriAttributes:
            tags = tree.xpath(uriAttribute[0])
            for tag in tags:
                if tag.attrib.get(uriAttribute[1]) is not None:
                    if urllib.parse.urlparse(tag.attrib[uriAttribute[1]]).scheme == '':
                        tag.attrib[uriAttribute[1]] = urllib.parse.urljoin(baseuri, tag.attrib[uriAttribute[1]])


class URLReceiver(Receiver):
    def __init__(self, uri, contenttype='html', encoding='utf-8', userAgent=None, accept=None):
        super().__init__(uri)
        self.contenttype = contenttype
        self.encoding = encoding
        self.userAgent = userAgent
        self.accept = accept

    # input: [Content], output: [Content]
    def performAction(self, contentList=None):
        if contentList is None:
            contentList = []
        
        # open website
        req = urllib.request.Request(self.uri)
        if self.userAgent is not None:
            req.add_header('User-Agent', self.userAgent)
        if self.accept is not None:
            req.add_header('Accept', self.accept)

        with urllib.request.urlopen(req) as thefile:
            filecontent = thefile.read().decode(self.encoding, errors='ignore')
            contentList.append(Content(uri=self.uri, encoding=self.encoding, title=None, content=filecontent, contenttype=self.contenttype))

        return contentList


class CommandReceiver(Receiver):
    def __init__(self, command, contenttype='text', encoding='utf-8'):
        super().__init__(command)
        self.encoding = encoding
        self.command = command
        self.contenttype = contenttype

    # input: [Content], output: [Content]
    def performAction(self, contentList=None):
        if contentList is None:
            contentList = []

        # run command and retrieve output
        process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, close_fds=True)
        thefile = process.stdout
        result = thefile.read().decode(self.encoding, errors='ignore')
        thefile.close()

        if process.wait() != 0:
            raise Exception("process terminated with an error: " + str(process.stderr) + "\n" + result)

        contentList.append(Content(uri=None, encoding=self.encoding, title=None, content=result, contenttype=self.contenttype))
        return contentList


class XPathParser(Parser):
    def __init__(self, contentxpath, titlexpath=None):
        self.contentxpath = contentxpath
        self.titlexpath = titlexpath

    # input: [Content], output: [Content]
    def performAction(self, contentList):
        result = []
        for content in contentList:
            result.extend(self.parseOneObject(content))
        return result

    # input: Content, output: [Content]
    def parseOneObject(self, content):
        baseuri = content.uri
        if content.contenttype == 'html':
            parser = etree.HTMLParser(encoding=content.encoding)
        else:
            parser = etree.XMLParser(recover=True, encoding=content.encoding)

        tree = etree.fromstring(content.content, parser=parser)

        # xpath
        contentresult = [] if self.contentxpath is None else tree.xpath(self.contentxpath)
        titleresult = [] if self.titlexpath is None else tree.xpath(self.titlexpath)

        # translate relative URIs to absolute URIs
        if content.contenttype == 'html':
            basetaglist = tree.xpath('/html/head/base')
            if len(basetaglist) != 0:
                baseuri = basetaglist[0].attrib['href']
            if len(contentresult) != 0:
                toAbsoluteURIs(contentresult, baseuri)
            if len(titleresult) != 0:
                toAbsoluteURIs(titleresult, baseuri)

        if self.contentxpath and len(contentresult) == 0:
            raise Exception('WARNING: content selector became invalid!')
        if self.titlexpath and len(titleresult) == 0:
            raise Exception('WARNING: title selector became invalid!')

        contents = []
        titles = []
        if isinstance(contentresult, str):
            contents = [contentresult]
        else:
            if len(contentresult) == 0:
                contentresult = titleresult
            contents = [etree.tostring(s, encoding=content.encoding, pretty_print=True).decode(content.encoding, errors='ignore') for s in contentresult]

        if isinstance(titleresult, str):
            titles = [getSubject(titleresult)]*len(contents)
        else:
            if len(titleresult) == 0 or len(titleresult) != len(contentresult):
                titleresult = contentresult
            titles = [getSubject(etree.tostring(s, method='text', encoding=content.encoding).decode(content.encoding, errors='ignore')) for s in titleresult]

        result = []
        for i in range(0, len(contents)):
            result.append(Content(uri=content.uri, encoding=content.encoding, title=titles[i], content=contents[i], contenttype=content.contenttype))

        return result


class CSSParser(Parser):
    def __init__(self, contentcss, titlecss=None):
        contentxpath = GenericTranslator().css_to_xpath(contentcss)
        titlexpath = None
        if titlecss is not None:
            titlexpath = GenericTranslator().css_to_xpath(titlecss)

        self.xpathparser = XPathParser(contentxpath=contentxpath, titlexpath=titlexpath)

    # input: [Content], output: [Content]
    def performAction(self, contentList):
        return self.xpathparser.performAction(contentList)


class RegExParser(Parser):
    def __init__(self, contentregex, titleregex=None):
        self.contentregex = contentregex
        self.titleregex = titleregex

    # input: [Content], output: [Content]
    def performAction(self, contentList):
        result = []
        for content in contentList:
            result.extend(self.parseOneObject(content))
        return result

    # input: Content, output: [Content]
    def parseOneObject(self, content):
        contents = []
        titles = []
        if self.contentregex is not None:
            for c in re.findall(r'' + self.contentregex, content.content, re.M):
                if len(c.strip()) != 0:
                    contents.append(c)
        if self.titleregex is not None:
            for c in re.findall(r'' + self.titleregex, content.title, re.M):
                if len(c.strip()) != 0:
                    titles.append(c)

        if self.contentregex is not None and len(contents) == 0:
            raise Exception('WARNING: content regex became invalid!')
        elif self.titleregex is not None and len(titles) == 0:
            raise Exception('WARNING: title regex became invalid!')
        else:
            if len(contents) == 0:
                contents = titles
            if len(titles) == 0 or len(titles) != len(contents):
                titles = [getSubject(c) for c in contents]

        result = []
        for i in range(0, len(contents)):
            result.append(Content(uri=content.uri, encoding=content.encoding, title=titles[i], content=contents[i], contenttype=content.contenttype))

        return result

