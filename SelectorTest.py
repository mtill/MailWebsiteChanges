#!/usr/bin/python

import sys
import MailWebsiteChanges

site = sys.argv   # invoke this script with e.g., "http://my-website-uri123.org/download/" "CSS-Selector" "regular expression"

print MailWebsiteChanges.parseSite(site[1], site[2], site[3])[0]

