import threading
import re
import socket
import sys
from socket import *

socket_server = socket(AF_INET, SOCK_STREAM)
socket_server.bind(('localhost', int(sys.argv[1])))
socket_server.listen(4)


if len(sys.argv) != 3:
    print("Usage: {} <port> <répertoire>".format(sys.argv[0]))
    sys.exit(1)

list = []

def traiter_client(sock_client):
    isconnected = False
    pseudo = ""
    message = sock_client.recv(1024)
    message = message.decode()
    request = re.compile(r"^(?P<command>[A-Z]+) (?P<variable>[a-zA-Z0-9]+)?")
    match = re.match(request, message)
    if (match is not None):
        answer = ""
        informationAllClient = ""
        informationClient = ""
        if(match.group("command") == "CONNECT"):
            answer, informationAllClient, informationClient = connect(match.group("variable"), isconnected, list)
        elif(match.group("command") == "QUIT"):
            answer = quit(match, isconnected, list, pseudo)
        else:
            pass
        sock_client.send((answer+'\n'+informationClient).encode())

def connect(pseudo, isconnected, list):
    request = re.compile(r"^(?P<pseudo>[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,pseudo)
    if (pseudo is None):
        answer = "403"
    elif (matchReq is None):
        answer = "408"
    elif (pseudo in list):
        answer = "405"
    elif (isconnected == True):
        answer = "400"
    else:
        answer = "200"
        informationAllClient = "*" + pseudo + " CONNECT"
        informationClient = "*" + " ".join(list)
        list.append(pseudo)
        isconnected = True
        return answer, informationAllClient, informationClient
    return answer, None, None

while True:
    try:
        sock_client, adr_client = socket_server.accept()
        print("Connection de : "+adr_client[0])
        threading.Thread(target=traiter_client, args=(sock_client,)).start()
    except KeyboardInterrupt:
        break