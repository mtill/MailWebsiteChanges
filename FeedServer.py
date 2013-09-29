#!/usr/bin/python3

import config
import http.server
import socketserver
import importlib
import sys

port = 8000

configMod = 'config'
if (len(sys.argv) > 1):
        configMod = sys.argv[1]
config = importlib.import_module(configMod)


handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(('', port), handler)

print('Listening on port ' + str(port))
httpd.serve_forever()

