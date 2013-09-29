#!/usr/bin/python3

import config
import http.server
import socketserver

port = 8000

handler = http.server.SimpleHTTPRequestHandler

httpd = socketserver.TCPServer(('', port), handler)

print('Listening on port ' + str(port))
httpd.serve_forever()

