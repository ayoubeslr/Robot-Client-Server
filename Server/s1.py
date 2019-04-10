import threading
import re
import socket
import sys
from socket import *
import random
from time import gmtime, strftime
import datetime

config = []
with open("spaceXserver.conf", 'r') as f:

    for line in f:
        config.append(line[:-1])

socket_server = socket(AF_INET, SOCK_STREAM)
socket_server.bind(('localhost', int(sys.argv[1])))
socket_server.listen(4)

# with open(config[2], 'a') as f:
#     now = strftime("%Y/%m/%d %H:%M:%S", gmtime())
#     f.write(f"{now}"+" Serveur started\n")
#     f.write(f"{now}"+" Listen on :"+config[0]+"\n")

liste = []
carteInfo = {}
resources = [1,2,5,0]

def initialiserCarte():
    i = 0
    j = 0
    for i in range (0,5):
        for j in range (0,5):
            carteInfo[(i,j)] = (random.choice(resources),str(0))
            j += 1
        i += 1
    return carteInfo

if len(sys.argv) != 3:
    print("Usage: {} <port> <répertoire>".format(sys.argv[0]))
    sys.exit(1)


def traiter_client(sock_client, adr_client):
    isconnected = False
    isCreateRobot = False
    pseudo = ""
    answer = ""
    informationAllClient = ""
    informationClient = ""
    deconnexion = False
    score = 0
    enPause = ""
    message = ""

    while deconnexion != True:
        try :
            messageC = sock_client.recv(1024)
            messageC = messageC.decode()
            with open("historique.txt", 'a') as f:
                now = strftime("%Y/%m/%d %H:%M:%S", gmtime())
                f.write(f"{now}"+messageC + " from " + str(adr_client[0])+":"+str(adr_client[1])+'\n')

            requete = re.compile(r"^(?P<command>[A-Z]+)(?P<variable>\s[a-zA-Z0-9]*)?")
            match = re.match(requete, messageC)
            if (match is not None):
                if(match.group("command") == "CONNECT"):
                    isconnected, pseudo, message = connecter(sock_client,match.group("variable"), isconnected, liste, message, carteInfo)

                elif(match.group("command") == "QUIT"):
                    deconnexion, isconnected, message = quitter(sock_client, pseudo, isconnected, liste, message)

                elif(match.group("command") == "CREATEROBOT"):
                    isCreateRobot, enPause, message = creerRobot(sock_client, match.group("variable"), match.group("variable"), pseudo, isconnected, isCreateRobot, carteInfo, score, enPause, message)
                    print(carteInfo)
                elif(match.group("command") == "MOVEROBOT"):
                    message = bougerRobot(sock_client,  match.group("variable"),  match.group("variable"), isconnected, isCreateRobot, pseudo, enPause, score, liste, message)
                    print(carteInfo)
                elif(match.group("command") == "PAUSEROBOT"):
                    enPause, message = pauseRobot(sock_client, isconnected, enPause, pseudo, message)
                
                elif(match.group("command") == "RESUMEROBOT"):
                    enPause, message = retirerPauseRobot(sock_client, isconnected, isCreateRobot, enPause, pseudo, message)

                elif(match.group("command") == "LIST"):
                    message = listerInfo(sock_client,isconnected,liste,message)

                elif(match.group("command") == "NICK"):
                    message = changerPseudo(sock_client, isconnected, pseudo, liste, match.group("variable"), message)
                
                else:
                    message += "Erreur"
            #message += '\n'
            
            sock_client.send(message.encode())
            message = ""
        except KeyboardInterrupt:
            break


def connecter(sock_client, pseudo, isconnected, liste, message, carteInfo):
    request = re.compile(r"^(?P<pseudo>\s[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,pseudo)
    pseudoConnect = pseudo
    print(pseudo)
    for name in liste:
        if name[0] == pseudo:
            answer = "405" #ERR_NICKNAMEINUSE : Nickname is already used
            message += answer
            
    if message != "405":
        if (pseudo is None):
            answer = "403" #ERR_NOTENOUGHARS : The request has not enough
            message += answer

        elif (matchReq is None):
            answer = "408" #ERR_INVALIDNICKNAME : The nickname is to long (max 15)
            message += answer
        
        elif isconnected == True:
            answer = "400" #ERR_ALREADYCONNECTED : The client is already connected
            message += answer
        
        else:
            answer = "200" #RPL_DONE : Success
            informationClient = "*" + pseudoConnect + " CONNECT"
            informationAllClient = "*"
            for name in liste:
                informationAllClient += name[0] + " "
            liste.append((pseudo,0))

            coordRobot = ""
            for clef, value in carteInfo.items():
                if value[1] != '0':
                    coordRobot += str(clef[0]) + ","+str(clef[1])+","

            isconnected = True

            message += answer+'\n'+informationClient+'\n'+informationAllClient+'\n'+coordRobot+'\n'+str(carteInfo)
        
    return isconnected, pseudo, message

def pauseRobot(sock_client, isconnected, enPause, pseudo, message):
    # Client must not be disconnected
    if(isconnected == False):
        answer = "401"
        sock_client.send(answer.encode())
    # The robot should not be paused
    elif(enPause == True):
        answer = "402"
        message += answer
    else:
        enPause = True
        answer = "203"
        informationClient = "*" + pseudo + " PAUSE ROBOT"
        message += answer+'\n'+informationClient
    return enPause, message

def quitter(sock_client, pseudo, isconnected, liste, message):
    if isconnected == True:
        isconnected == False
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " QUIT"
        message += answer+'\n'+informationClient
        for name in liste:
            if pseudo == name[0]:
                liste.remove(name)
        #liste.remove(pseudo)
        deconnexion = True

    else:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        message += answer
        #deconnexion = False

    return deconnexion, isconnected, message

def creerRobot(sock_client, ligne, colonne, pseudo, isconnected, isCreateRobot, carteInfo, score, enPause, message):
    coordonnee = (int(ligne),int(colonne))
    if (int(ligne) > 5 or int(colonne )> 5 or int(ligne) < 0 or int(colonne) < 0):
        answer = "407"
        message += answer

    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED The client is not connected
        message += answer
        isCreateRobot = False
        enPause = True

    else:
        if isconnected == True:
            for clef,val in carteInfo.items():
                if clef == coordonnee:
                    if val[1] == "0":
                        score += val[0]
                        carteInfo[clef] = (0,pseudo)
                        print(pseudo)
                        print(carteInfo[clef])
                        # Mise à jour des informations des joueurs
                        for name in liste:
                            if name[0] ==  pseudo:
                                name2 = (pseudo, score)
                                liste.remove(name)
                                liste.append(name2)

                        answer = "202" #ROBOT_CREATED : Create a new robot
                        informationClient = "*" + pseudo + " CREATEROBOT"
                        message += answer+'\n'+informationClient
                        isCreateRobot = True
                        enPause = False

                    else:
                        answer = "406" #ERR_SQUARETAKEN : It already taken by another robot
                        message += answer

    return isCreateRobot, enPause, message

def bougerRobot(sock_client, variable, variable2, isconnected, isCreateRobot, pseudo, enPause, score, liste, message):
    find = 0
    if(isconnected == False):
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        message += answer
   
    elif(isCreateRobot == False):
        answer = "409" #ROBOT_DESACTIVED : The client must have already created a robot
        message += answer
    
    elif(enPause == True):
        answer = "402" #ERR_BADSTATUS : The robot was not away
        message += answer
    else:
        coord = (int(variable), int(variable2))

        # Sert à modifier le score du client car gain de score ou non
        for clef, value in carteInfo.items():
            if(value[1] == pseudo):
                if ((coord[0] - clef[0] <= 1) and (coord[0] - clef[0] >= -1) and (coord[1] - clef[1] <= 1) and (coord[1] - clef[1] >= -1)):
                    res = value[0]
                    carteInfo[clef] = (res, "0")
                    for clef, value in carteInfo.items():
                        if (clef == coord):
                            find += 1
                            if(value[1] != "0"):
                                answer = "406" #ERR_SQUARETAKEN : It already taken by another robot
                                message += answer
                            else:
                                score += value[0]
                                carteInfo[clef] = (0, pseudo)
                                for name in liste:
                                    if name[0] ==  pseudo:
                                        name2 = (pseudo, score)
                                        liste.remove(name)
                                        liste.append(name2)
                                informationClient = ""
                                for clef, value in carteInfo.items():
                                    if value[1] != '0':
                                        informationClient += str(clef[0]) + ","+str(clef[1])+","
                                answer = "203" #MOVE_ROBOT : Robot has moved
                                message += answer+'\n'+informationClient

        if(find == 0):
            answer = "407" #ERR_SQUARENOTFOUND : The square does not exist
            message += answer
        print(carteInfo)
    return message

def retirerPauseRobot(sock_client, isconnected, isCreateRobot, enPause, pseudo, message):

    if isCreateRobot == False:
        answer = "409" #ROBOT_DESACTIVED : The robot it's not created
        message += answer

    elif enPause == False:
        answer = "402" #ERR_BADSTATUS : The robot was not away
        message += answer

    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        message += answer

    else:
        answer = "200" #RPL_DONE : Success
        informationClient = "*" + pseudo + " RESUMEROBOT"
        #sock_client.send((answer+'\n'+informationClient+'\n').encode())
        message += answer+'\n'+informationClient+'\n'
        enPause = False

    return enPause, message

def listerInfo(sock_client, isconnected, liste, message):
    if isconnected == True:
        answer = "201" #ROBOT_NAMES : Returns a list of pseudo
        info = "*"
        for informations in liste:
            info += str(informations) + " "
        message += answer+'\n'+info
        print(liste)
    else:
        answer = "401" # ERR_NOTCONNECTED : The client is not connected
        message += answer
    
    return message

def changerPseudo(sock_client, isconnected, pseudo, liste, nouveauPseudo,message):
    request = re.compile(r"^(?P<pseudo>[a-zA-Z0-9]{1,15})?")
    matchReq = re.match(request,nouveauPseudo)
    for name in liste:
        if name[0] == nouveauPseudo:
            answer = "405" #ERR_NICKNAMEINUSE : Nickname is already used
            #sock_client.send((answer+'\n').encode())
            message += answer 

    if (nouveauPseudo is None):
        answer = "403" #ERR_NOTENOUGHARS : The request has not enough
        #sock_client.send((answer+'\n').encode())
        message += answer

    elif (matchReq is None):
        answer = "408" #ERR_INVALIDNICKNAME : The nickname is to long (max 15)
        #sock_client.send((answer+'\n').encode())
        message += answer
    
    elif isconnected == False:
        answer = "401" #ERR_NOTCONNECTED : The client is not connected
        #sock_client.send((answer+'\n').encode())
        message += answer

    elif isconnected == True:
        answer = "200" #RPL_DONE : Succes
        for clef,val in carteInfo.items():
            if val[1] == pseudo:
                ressource = val[0]
                carteInfo[clef] = (ressource,nouveauPseudo)

        for name in liste:
            if name[0] == pseudo:
                score = name[1]
                name2 = (nouveauPseudo, name[1])
                liste.remove(name)
                liste.append(name2)
                print(liste)


        informationClient = "*" + pseudo + " NICK" + nouveauPseudo
        message += answer+'\n'+informationClient
    
    return message

initialiserCarte()

while True:
    try:
        sock_client, adr_client = socket_server.accept()
        print("Connection de : "+adr_client[0])
        threading.Thread(target=traiter_client, args=(sock_client, adr_client)).start()
    except KeyboardInterrupt:
        break


print("Fin du serveur.")
socket_server.shutdown(SHUT_RDWR)
socket_server.close()
sys.exit(0)