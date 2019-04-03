import sys
from socket import *


socket_client = socket(AF_INET, SOCK_STREAM) 
socket_client.connect(("localhost", 8002))

def connecter(pseudo):
    chaine = "CONNECT " + pseudo
    print(chaine)
    socket_client.send(chaine.encode())
    

TAILLE_TAMPON = 256


print('Deconnexion.')



