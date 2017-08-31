# Copyright: (2013-2014) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+

#We collect xpath snippets at this place: <a href="https://github.com/Debianguru/MailWebsiteChanges/wiki/snippets">Snippet collection</a> - please feel free to add your own definitions!



from mwctools import URLReceiver as uri
from mwctools import CommandReceiver as command
from mwctools import XPathParser as xpath
from mwctools import CSSParser as css
from mwctools import RegExParser as regex
from mwctools import Content
from mwctools import Parser

import os.path


sites = [

         {'name': 'example-css',
          'parsers': [uri(uri='https://github.com/mtill', contenttype='html'),
                      css(contentcss='div')
                     ]
         },

         {'name': 'example-xpath',
          'parsers': [uri(uri='https://example-webpage.com/test', contenttype='html'),
                      xpath(contentxpath='//div[contains(concat(\' \', normalize-space(@class), \' \'), \' package-version-header \')]')
                     ]
         },

         {'name': 'my-script',
          'parsers': [command(command='/home/user/script.sh', contenttype='text'),
                      regex(contentregex='^.*$')
                     ]
         }

]

#os.chdir('/path-to-data-dir/MailWebsiteChanges-data')

enableMailNotifications = False
maxMailsPerSession = -1
sender = 'me@mymail.com'
smtphost = 'mysmtpprovider.com'
useTLS = True
smtpport = 587
smtpusername = sender
smtppwd = 'mypassword'
receiver = 'me2@mymail.com'

enableRSSFeed = False
rssfile = 'feed.xml'
maxFeeds = 100

