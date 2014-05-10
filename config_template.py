import os.path

# Copyright: (2013-2014) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+

#We collect xpath snippets at this place: <a href="https://github.com/Debianguru/MailWebsiteChanges/wiki/snippets">Snippet collection</a> - please feel free to add your own definitions!

sites = [

          {'shortname': 'mywebsite1',
           'uri': 'http://www.mywebsite1.com/info',
           'type': 'html',
           'titlexpath': '//h1',
           'contentxpath': '//div',
           'titleregex': '',
           'contentregex': '',
           'encoding': 'utf-8'},

          {'shortname': 'mywebsite2',
           'uri': 'http://www.mywebsite2.com/info',
           'type': 'html',
           'contentxpath': '//*[contains(concat(\' \', normalize-space(@class), \' \'), \' news-list-container \')]',
           'regex': '',
           'encoding': 'utf-8'},

          {'shortname': 'mywebsite3',
           'uri': 'http://www.mywebsite3.com/info',
           'type': 'text',
           'contentxpath': '',
           'contentregex': 'Version\"\:\d*\.\d*',
           'encoding': 'utf-8'},

          {'shortname': 'lscmd',
           'uri': 'cmd://ls -l /home/pi',
           'contentregex': '.*Desktop.*'
          }

]

subjectPostfix = 'A website has been updated!'

enableMailNotifications = True
sender = 'me@mymail.com'
smtphost = 'mysmtpprovider.com'
useTLS = True
smtpport = 587
smtpusername = sender
smtppwd = 'mypassword'
receiver = 'me2@mymail.com'

os.chdir('/var/cache/mwc')

enableRSSFeed = True
rssfile = 'feed.xml'
maxFeeds = 100

