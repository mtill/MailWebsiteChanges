#!/usr/bin/python

import sys
import func

site = sys.argv   # invoke this script with e.g., "http://www.rockbox.org/download/" "CSS-Selector" "regular expression"

print site[1]

print func.parseSite(site)

