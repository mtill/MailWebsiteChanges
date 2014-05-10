#!/usr/bin/python3

# Copyright: (2013-2014) Michael Till Beck <Debianguru@gmx.de>
# License: GPL-2.0+

import http.server
import socketserver
import importlib
import sys
import getopt

bind = 'localhost'
port = 8000
configMod = 'config'


try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:b:p:', ['help', 'config=', 'bind=', 'port='])
except getopt.GetoptError:
        print('Usage: FeedServer.py --config=config --port=8000')
        sys.exit(1)

for opt, arg in opts:
        if opt == '-h':
                print('Usage: FeedServer.py --config=config --bind=localhost --port=8000')
                exit()
        elif opt in ('-c', '--config'):
                configMod = arg
        elif opt in ('-b', '--bind'):
                bind = arg
        elif opt in ('-p', '--port'):
                port = int(arg)

config = importlib.import_module(configMod)


handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer((bind, port), handler)

print('Bond to ' + bind + ', listening on port ' + str(port))
httpd.serve_forever()

