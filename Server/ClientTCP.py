import socket
import sys

HOST = "192.168.43.71"
PORT = int(sys.argv[1])

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Connexion vers " + HOST + ":" + str(PORT) + " reussie.")

while True :
        try :
                message = input("Requete : ")
                message = str(message)
                print('Envoi de : ' + str(message))
                n = client.send(message.encode())
                if (n != len(message)):
                        print('Erreur envoi.')
                else:
                        print('Envoi ok.')

                print('Reception...')
                donnees = client.recv(2048)
                print(donnees)
                print('Recu :', donnees.decode())
        except KeyboardInterrupt:
                break

print('Deconnexion du client.')
client.close()
