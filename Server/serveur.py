import threading
import re
import socket
import sys
from socket import *
import random

socket_server = socket(AF_INET, SOCK_STREAM)
socket_server.bind(('localhost', int(sys.argv[1])))
socket_server.listen(4)

liste = []
carteInfo = {}
resources = [1,2,5,0]

def initialiserCarte():
    i = 0
    j = 0
    for i in range (0,15):
        for j in range (0,15):
            carteInfo[(i,j)] = (random.choice(resources),str(0))
            j += 1
        i += 1
    return carteInfo

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
    score = 0
    enPause = True

    while deconnexion != True:
        try :
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
                    isCreateRobot, enPause = creerRobot(sock_client, match.group("variable"), match.group("variable2"), pseudo, isconnected, isCreateRobot, carteInfo, score, enPause)
                
                elif(match.group("command") == "MOVEROBOT"):
                    pass
                
                elif(match.group("command") == "PAUSEROBOT"):
                    enPause = pauseRobot(sock_client, isconnected, enPause, pseudo)
                
                elif(match.group("command") == "LIST"):
                    listerInfo(sock_client,isconnected,liste)

                elif(match.group("command") == "NICK"):
                    changerPseudo(sock_client, isconnected, pseudo, liste, match.group("variable"))
        except KeyboardInterrupt:
            break


def connecter(sock_client, pseudo, isconnected, liste):
    request = re.compile(r"^(?P<pseudo>[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,pseudo)

    for name in liste:
        if name[0] == pseudo:
            answer = "405" #ERR_NICKNAMEINUSE : Nickname is already used
            sock_client.send((answer+'\n').encode())
            exit(0)

    if (pseudo is None):
        answer = "403" #ERR_NOTENOUGHARS : The request has not enough
        sock_client.send((answer+'\n').encode())

    elif (matchReq is None):
        answer = "408" #ERR_INVALIDNICKNAME : The nickname is to long (max 15)
        sock_client.send((answer+'\n').encode())
    
    elif isconnected == True:
        answer = "400" #ERR_ALREADYCONNECTED : The client is already connected
        sock_client.send((answer+'\n').encode())
    
    else:
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " CONNECT"
        informationAllClient = "*"
        for name in liste:
            informationAllClient += name[0] + " "
        liste.append((pseudo,""))
        isconnected = True
        sock_client.send((answer+'\n'+informationClient+'\n'+informationAllClient).encode())
        
    return isconnected, pseudo

def quitter(sock_client, pseudo, isconnected, liste):
    if isconnected == True:
        isconnected == False
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " QUIT"
        sock_client.send((answer+'\n'+informationClient).encode())
        liste.remove(pseudo)
        deconnexion = True
        sock_client.close()

    else:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        sock_client.send((answer+'\n').encode())
        deconnexion = False

    return deconnexion, isconnected

def creerRobot(sock_client, ligne, colonne, pseudo, isconnected, isCreateRobot, carteInfo, score, enPause):
    requete = re.compile(r"^(?P<coord>\s[0-9\s0-9])?")
    coordonnee = ligne + colonne
    matchReq = re.match(requete,coordonnee)
    coordonnee = (int(ligne),int(colonne))
    print(coordonnee)
    print(carteInfo)

    if isconnected == False:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        sock_client.send((answer+'\n').encode())

    elif (matchReq is None):
        answer = "407" #ERR_SQUARENOTFOUND : The square does not exist
        sock_client.send((answer+'\n').encode())

    else:
        if isconnected == True:
            for clef,val in carteInfo.items():
                if clef == coordonnee:
                    if val[1] == "0":
                        score += val[0]
                        carteInfo[clef] = (0,pseudo)

                        # Mise à jour des informations des joueurs
                        for name in liste:
                            if name[0] ==  pseudo:
                                name2 = (pseudo, score)
                                liste.remove(name)
                                liste.append(name2)

                        answer = "202" #ROBOT_CREATED : Create a new robot
                        informationClient = "*" + pseudo + " CREATEROBOT"
                        sock_client.send((answer+'\n'+informationClient).encode())
                        isCreateRobot = True
                        enPause = False

                    else:
                        answer = "406" #ERR_SQUARETAKEN : It already taken by another robot
                        sock_client.send((answer+'\n').encode())

    return isCreateRobot, enPause

def bougerRobot():
    pass

def pauseRobot(sock_client, isconnected, enPause, pseudo):
    if enPause == True:
        answer = "402" #ERR_BADSTATUS : The robot was not away
        sock_client.send((answer+'\n').encode())

    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        sock_client.send((answer+'\n').encode())
    
    else:
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " PAUSE"
        sock_client.send((answer+'\n'+informationClient+'\n').encode())

    return enPause

def retirerPauseRobot(sock_client, isconnected, enPause, pseudo):
    if enPause == False:
        answer = "402" #ERR_BADSTATUS : The robot was not away
        sock_client.send((answer+'\n').encode())

    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        sock_client.send((answer+'\n').encode())
    
    else:
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " PAUSE"
        sock_client.send((answer+'\n'+informationClient+'\n').encode())

    return enPause

def listerInfo(sock_client, isconnected, liste):
    if isconnected == False:
        answer = "401" # ERR_NOTCONNECTED : The client is not connected
        sock_client.send((answer+'\n').encode())
    else:
        answer = "201" #ROBOT_NAMES : Returns a list of pseudo
        info = "*"
        for informations in liste:
            info += str(informations) + " "
        sock_client.send((answer+'\n'+info+'\n').encode())

def changerPseudo(sock_client, isconnected, pseudo, liste, nouveauPseudo):
    request = re.compile(r"^(?P<pseudo>[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,nouveauPseudo)
    print(liste)
    for name in liste:
        if name[0] == nouveauPseudo:
            answer = "405" #ERR_NICKNAMEINUSE : Nickname is already used
            sock_client.send((answer+'\n').encode())
            exit(0)

    if (nouveauPseudo is None):
        answer = "403" #ERR_NOTENOUGHARS : The request has not enough
        sock_client.send((answer+'\n').encode())

    elif (matchReq is None):
        answer = "408" #ERR_INVALIDNICKNAME : The nickname is to long (max 15)
        sock_client.send((answer+'\n').encode())
    
    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        sock_client.send((answer+'\n').encode())

    elif isconnected == True:
        answer = "200" #RPL_DONE : Succes
        for clef,val in carteInfo.items():
            if val[0] == pseudo:
                ressource = val[1]
                carteInfo[clef] = (nouveauPseudo,ressource)

        for name in liste:
            if name[0] == pseudo:
                score = name[1]
                name2 = (nouveauPseudo, name[1])
                liste.remove(name)
                liste.append(name2)
                print(liste)
        informationClient = "*" + pseudo + " NICK " + nouveauPseudo
        sock_client.send((answer+'\n'+informationClient+'\n').encode())

initialiserCarte()

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