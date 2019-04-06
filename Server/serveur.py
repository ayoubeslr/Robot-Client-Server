import threading
import re
import socket
import sys
from socket import *

socket_server = socket(AF_INET, SOCK_STREAM)
socket_server.bind(('localhost', int(sys.argv[1])))
socket_server.listen(4)

liste = []
carteInfo = {}


if len(sys.argv) != 3:
    print("Usage: {} <port> <répertoire>".format(sys.argv[0]))
    sys.exit(1)


def traiter_client(sock_client):
    isconnected = False
    isCreateRobot = False
    pseudo = ""
    answer = ""
    informationAllClient = ""
    informationClient = ""
    deconnexion = False

    while deconnexion != True:
        message = sock_client.recv(1024)
        message = message.decode()
        requete = re.compile(r"^(?P<command>[A-Z]+)(?P<variable>\s[a-zA-Z0-9]*)(?P<variable2>\s[a-zA-Z0-9]*)?")
        match = re.match(requete, message)
        if (match is not None):
            if(match.group("command") == "CONNECT"):
                isconnected, pseudo = connecter(sock_client,match.group("variable"), isconnected, liste)

            elif(match.group("command") == "QUIT"):
                deconnexion, isconnected = quitter(sock_client, pseudo, isconnected, liste)

            elif(match.group("command") == "CREATEROBOT"):
                isCreateRobot, isconnected = creerRobot(sock_client, match.group("variable2"), pseudo, isconnected, isCreateRobot, carteInfo)
                print(carteInfo)
    
    sock_client.close()


def connecter(sock_client, pseudo, isconnected, liste):
    request = re.compile(r"^(?P<pseudo>[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,pseudo)

    if (pseudo is None):
        answer = "403" #ERR_NOTENOUGHARS : The request has not enough
        sock_client.send((answer+'\n').encode())

    elif (matchReq is None):
        answer = "408" #ERR_INVALIDNICKNAME : The nickname is to long (max 15)
        sock_client.send((answer+'\n').encode())

    elif pseudo in liste:
        answer = "405" #ERR_NICKNAMEINUSE : Nickname is already used
        sock_client.send((answer+'\n').encode())
 
    elif isconnected != True:
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " CONNECT"
        informationAllClient = "*" + " ".join(liste)
        liste.append(pseudo)
        isconnected = True
        sock_client.send((answer+'\n'+informationClient+'\n'+informationAllClient).encode())

    elif isconnected != False:
        answer = "400" #ERR_ALREADYCONNECTED : The client is already connected
        sock_client.send((answer+'\n').encode())
    
    return isconnected, pseudo

def quitter(sock_client, pseudo, isconnected, liste):
    if isconnected == True:
        isconnected == False
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " QUIT"
        sock_client.send((answer+'\n'+informationClient).encode())
        liste.remove(pseudo)
        deconnexion = True

    else:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        sock_client.send((answer+'\n').encode())
        deconnexion = False

    return deconnexion, isconnected

def creerRobot(sock_client, coord, isconnected, pseudo, isCreateRobot, carteInfo):
    requete = re.compile(r"^(?P<variable2>\s[0-9\s0-9])?")
    matchReq = re.match(requete,coord)

    if (pseudo is None):
        answer = "403" #ERR_NOTENOUGHARS : The request has not enough
        sock_client.send((answer+'\n').encode())

    elif (matchReq is None):
        answer = "407" #ERR_SQUARENOTFOUND : The square does not exist
        sock_client.send((answer+'\n').encode())

    elif isconnected == True:
        if len(carteInfo.keys()) == 0:
            
            carteInfo[str(coord)] = {'0',pseudo}
            answer = "202" #ROBOT_CREATED : Create a new robot
            informationClient = "*" + pseudo + " CREATEROBOT"
            sock_client.send((answer+'\n'+informationClient).encode())
            isCreateRobot = True

        else:
            for clef in carteInfo:
                for valeur in clef.values():
                    if  valeur == pseudo:
                        answer = "409" #ROBOT_ALREADYCREATED : Robot already created
                        sock_client.send((answer+'\n').encode())

                    elif valeur == '0' :
                        carteInfo['coord'] = {'0',pseudo}
                        answer = "202" #ROBOT_CREATED : Create a new robot
                        informationClient = "*" + pseudo + " CREATEROBOT"
                        sock_client.send((answer+'\n'+informationClient).encode())
                        isCreateRobot = True

                    elif valeur != '0':
                        answer = "406" #ERR_SQUARETAKEN : It already taken by another robot
                        sock_client.send((answer+'\n').encode())

    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        sock_client.send((answer+'\n').encode())

    return isCreateRobot, isconnected


while True:
    try:
        sock_client, adr_client = socket_server.accept()
        print("Connection de : "+adr_client[0])
        threading.Thread(target=traiter_client, args=(sock_client,)).start()
    except KeyboardInterrupt:
        break


print("Fin du serveur.")
socket_server.shutdown(SHUT_RDWR)
socket_server.close()
sys.exit(0)