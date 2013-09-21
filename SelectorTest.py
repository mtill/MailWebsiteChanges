#!/usr/bin/python

import sys
import MailWebsiteChanges

# URI | content type | XPath | regular expression | encoding
site = sys.argv   # invoke this script with e.g., "http://my-website-uri123.org/download/" "html" "XPath-Selector" "regular expression" "encoding"

print MailWebsiteChanges.parseSite(site[1], site[2], site[3], site[4], site[5])['content']

