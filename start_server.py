from core import server
import socket
from threading import Thread

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 8080))
s.listen(1)

while True:
    conn, _ = s.accept()
    tcpserver = server.MYTCPServer(conn)
    p = Thread(target=tcpserver.run)
    p.start()
