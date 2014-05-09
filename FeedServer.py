#!/usr/bin/python3

# Copyright: (2013-2014) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+

import http.server
import socketserver
import importlib
import sys
import getopt

port = 8000
configMod = 'config'


try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:p:', ['help', 'config=', 'port='])
except getopt.GetoptError:
        print('Usage: FeedServer.py --config=config --port=8000')
        sys.exit(1)
for opt, arg in opts:
        if opt == '-h':
                print('Usage: FeedServer.py --config=config --port=8000')
                exit()
        elif opt in ('-c', '--config'):
                configMod = arg
        elif opt in ('-p', '--port'):
                port = int(arg)

config = importlib.import_module(configMod)


handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(('', port), handler)

print('Listening on port ' + str(port))
httpd.serve_forever()

