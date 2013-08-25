MailWebsiteChanges
==================

Python script to keep track of website changes (or changes of parts of websites); sends email notifications on updates

To specify which parts of a website should be monitored, <em>both CSS selectors</em> (e.g. "p .theClass") <em>or regular expressions can be used</em>.


<em>Requires</em> BautifulSoup and soupselect (http://code.google.com/p/soupselect/).

Configuration can be done by editing the MailWebsiteChanges.py file:
Some examples (use "html" to enable CSS selector mode or "text to use regular expressions):
<pre>
<code>
    sites = [['rockbox', 'http://www.rockbox.org/download/', 'html', 'h1'],
         ['calibre', 'http://calibre-ebook.com/download_linux', 'html', '#content p'],
         ['Firmware', 'http://www.examplevendorsite1.com/firmware', 'text', 'Version\"\:\d*\.\d*']
        ]
</code>
</pre>


<em>SelectorTest.py</em> might be useful in order to test the definitions before integrating them into the main script.

