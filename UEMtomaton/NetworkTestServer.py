import socket

commDelayStat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

commDelayStat_server.bind(('localhost',6666))

commDelayStat_server.listen(1)

comm, res = commDelayStat_server.accept()
print(comm)
print(res)

print(commDelayStat_server)
print("Connected")

asdf = comm.recv(1024)

print(asdf.decode())
print(asdf)

comm.send(b"meow")