import socket
import sys, threading, os, os.path, re
ADRESSE = ''
PORT = 8002

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind((ADRESSE, PORT))
serveur.listen(4)
client, adresseClient = serveur.accept()
print ('Connexion de ', adresseClient)

donnees = client.recv(1024)
donnees1= donnees.decode()
if not donnees:
        print('Erreur de reception.')
else:
        print ('Reception de:'+ donnees1)

        reponse = donnees1.upper()
        reponse1 = reponse.encode()
        print ('Envoi de :' + str(reponse1))
        n = client.send(reponse1)
        if (n != len(reponse1)):
                print ('Erreur envoi.')
        else:
                print ('Envoi ok.')


print ('Fermeture de la connexion avec le client.')
client.close()
print ('Arret du serveur.')
serveur.close()
