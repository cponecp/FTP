from core import server


tcpserver = server.MYTCPServer(('127.0.0.1',8080))
tcpserver.run()
