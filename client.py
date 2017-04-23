#!/usr/bin/env python
# coding: utf-8

import socket, sys, select, signal

##USEFUL TEXT
def redPrint(string):
	sys.stdout.write('\033[31m{}\033[0m\n'.format(string))

def closeClient(signal, frame):
	#On envoi au serveur notre intention de quitter le salon
	#try :
	clientSocket.send('/exit'.encode())
	try :
		clientSocket.close()
	except : pass
	redPrint('Vous vous êtes deconnecte du serveur.')
	#except : pass
	sys.exit(0)
        

def sendToServer(message):
	try :
		clientSocket.send(message.encode())
	except socket.error :
		redPrint('Le message n\'a pas peu etre envoye.')

##CLIENT-CONFIG##
serverAdress = sys.argv[1]
serverPort = int(sys.argv[2])
clientName = sys.argv[3]


#Creation du socket client
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connexion du socket au serveur
try :
	clientSocket.connect((serverAdress, serverPort))

except socket.error :
	redPrint('Impossible de se connecter a l\'hote distant')
	sys.exit(0)

#Le premier message envoye est le pseudo de l'utilisateur
clientSocket.send(clientName.encode())

#A faire en cas de ctrl-c
signal.signal(signal.SIGINT, closeClient)

#Liste de ports d'écoute (int, 0)
liste_lecture = [clientSocket, sys.stdin]

while True :
	readers,writers,errors = select.select(liste_lecture, [],[],0.1)
	
	for input in readers :
		#Si le message provient du serveur distant -> on l'affiche
		if input == clientSocket :
			message_entrant = clientSocket.recv(255).decode()
			
			if message_entrant == '/exit':
				closeClient(signal.SIGINT,0)
			sys.stdout.write(message_entrant)
			
		#Si il y a une entree sur stdin -> on envoi le message au serveur
		if input == sys.stdin :
			message_sortant = sys.stdin.readline()
			
			# message_sortant = 0 si EOF
			if message_sortant or message_sortant != '':
				sendToServer(message_sortant)
			else :
				closeClient(signal.SIGINT,0)
				
