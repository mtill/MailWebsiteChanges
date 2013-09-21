#!/usr/bin/python

import config
import SimpleHTTPServer
import SocketServer

port = 8000

handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(('', port), handler)

print 'Listening on port ' + str(port)
httpd.serve_forever()

