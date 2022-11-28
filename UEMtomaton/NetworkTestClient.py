import socket

delayStat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

connectResult = delayStat_client.connect(('127.0.0.1', 6666))

print(connectResult)

sender = "Meow"
delayStat_client.send(sender.encode())

asdf = delayStat_client.recv(1024)

print(asdf.decode())