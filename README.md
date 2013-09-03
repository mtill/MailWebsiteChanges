# MailWebsiteChanges

Python script to keep track of website changes (or changes of parts of websites); sends email notifications on updates

To specify which parts of a website should be monitored, <b>both CSS selectors</b> (e.g. "p .theClass") <b>and regular expressions can be used</b>.

## Configuration
Configuration can be done by creating a <code>config.py</code> file:
Some examples:
<pre>
<code>
 short name | URI [| CSS selector] [| regular expression]

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
</code>
</pre>

<em>SelectorTest.py</em> might be useful in order to test the definitions before integrating them into the config file.

## Requirements
<b>Requires</b> <a href="http://www.crummy.com/software/BeautifulSoup/">BeautifulSoup</a> and <a href="http://code.google.com/p/soupselect/">soupselect</a>.

