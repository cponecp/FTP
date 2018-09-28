from core.server import *

ftpserver = socketserver.ThreadingTCPServer(('127.0.0.1', 8080), MYTCPServer)
ftpserver.serve_forever()
