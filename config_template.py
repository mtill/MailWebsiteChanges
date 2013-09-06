import os.path

# remember to rename this file to "config.py"
# some examples (short name | URI [| CSS selector] [| regular expression])
sites = [['shortname1', 'http://www.mywebsite1.com/info', 'h1', ''],
         ['shortname2', 'http://www.mywebsite2.com/info', '.theClass > h3', ''],
         ['shortname3', 'http://www.mywebsite3.com', '', 'Version\"\:\d*\.\d*']
        ]

subjectPostfix = 'A website has been updated!'
sender = 'me@mymail.com'
smtptlshost = 'mysmtpprovider.com'
smtptlsport = 587
smtptlsusername = sender
smtptlspwd = 'mypassword'
receiver = 'me2@mymail.com'

os.chdir('/path/to/working/directory')

rssfile = 'feed.xml'   # set to '' if you don't want the script to generate a RSS2 feed

