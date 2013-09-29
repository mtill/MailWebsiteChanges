import os.path

sites = [

          {'shortname': 'mywebsite1',
           'uri': 'http://www.mywebsite1.com/info',
           'type': 'html',
           'xpath': '//h1',
           'regex': '',
           'encoding': 'utf-8'},

          {'shortname': 'mywebsite2',
           'uri': 'http://www.mywebsite2.com/info',
           'type': 'html',
           'xpath': '//*[contains(concat(\' \', normalize-space(@class), \' \'), \' news-list-container \')]',
           'regex': '',
           'encoding': 'utf-8'},

          {'shortname': 'mywebsite3',
           'uri': 'http://www.mywebsite3.com/info',
           'type': 'text',
           'xpath': '',
           'regex': 'Version\"\:\d*\.\d*',
           'encoding': 'utf-8'}

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

os.chdir('/path/to/data/directory')

enableRSSFeed = True
rssfile = 'feed.xml'
maxFeeds = 100

