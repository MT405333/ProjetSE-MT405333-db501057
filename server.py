#!/usr/bin/env python
# coding: utf-8

import socket, sys, select,signal

### STUFF

## AFFICHAGE
def colorString(color, string):
	if color == 'red' :
		return '\033[31m{}\033[0m\n'.format(string)
	elif color == 'green' :
		return '\033[92m{}\033[0m\n'.format(string)
	elif color == 'blue' :
		return '\033[94m{}\033[0m\n'.format(string)
	else :
		return string + '\n'

#Affiche sur l'entree standard un message
def sysPrint(string):
	sys.stdout.write("{}".format(string))

## MESSAGE
#Fonction d'envoi d'un message a tous les utilisateurs connectes
def send2All (connectedUsers, message):
	for user in connectedUsers.keys() :
		try :
			user.send(message.encode())
		except : pass

#Retourne un objet socket associe a un nom d'utilisateur unique		
def getSocketFromName(connectedUsers, userName):
	return list(connectedUsers.keys())[list(connectedUsers.values()).index(userName)]

#Differentes fonctions de formatage
def onConnMessage(userName):
	return '<{}> vient de se connecter !'.format(userName)

def onDeconnMessage(userName):
	return '<{}> s\'est deconnecte'.format(userName)

def onChangeNameMsg(userName, newUserName):
	return '<{}> se nomme maintenant <{}>'.format(userName,newUserName)


## GESTION DU FICHIER DE L'HISTORIQUE
def addMessageHistory(historyPath, message):
	#on lit la premiere ligne du fichier (semblable a un pop sur une fille)
	#puis on ecrit les lignes restante "en haut" du fichier
	while (sum(1 for line in open(historyPath, 'r')) >= 5) :
		old = open(historyPath, 'r')
		old.readline()
		newtext = old.read()
		old.close()
		newf = open(historyPath, 'w')
		newf.write(newtext)
		newf.close()
	#On ajoute ensuite a la fin du fichier le message receptionne
	history = open(historyPath, 'a')
	history.write(message)
	history.close()


## Handler en cas d'interruption Ctrl-C
def closeServer(signal, frame):
	global connectedUsers
	#Dans le cas ou des clients serait encore connecte
	for client in connectedUsers.keys() :
		client.send('/exit'.encode())
		client.close()
		sysPrint('\nLe client <{}> a ete deconnecte\n'.format(connectedUsers[client]))
		
	
	serveurSocket.close()
		
	if webOnline :
		webSocket.close()

	sysPrint(colorString('red', 'Le serveur a ete deconnecte'))
	sys.exit()


###INIT-SERVER###

#On initialise le dictionnaire des utilisateurs
connectedUsers = {}

#configuration du port IRC
try :
	serverPort = int(sys.argv[1])
except ValueError :
	printRed("Adresse de port du serveur IRC non renseignee ou invalide")

#On suppose le côté web optionnel
# si le port n'est pas renseigne -> pas de web
try :
	webPort = int(sys.argv[2])
	webOnline = True
	#On creer le fichier historique (dossier courant)
	history = open('history','a')
	history.close()
except :
	webOnline = False

## SOCKETS

# Socket IRC
serveurSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveurSocket.bind(("", serverPort))
serveurSocket.listen(10)
inputList = [serveurSocket]

launchMessage = 'Serveur IRC connecte : localhost:{}'.format(serverPort)

# Socket IRC
if webOnline :
	webSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	webSocket.bind(("", webPort))
	webSocket.listen(5)
	inputList.append(webSocket)
	
	launchMessage = launchMessage + '\nServeur Web connecte : localhost:{}'.format(webPort)
	
#Affichage sur le serveur du bon deploiement des sockets
sys.stdout.write(colorString('green',launchMessage + '\n================='))

#A faire en cas de ctrl-c
signal.signal(signal.SIGINT, closeServer)
		

while True:
	
	incomConn, wlist, xlist = select.select(inputList, [], [],0.1)
	
	for connection in incomConn :
		for input in incomConn :
			if webOnline and input == webSocket:
				
				clientweb, info = connection.accept()
				request = clientweb.recv(255).decode()
				path = request.split(' ')[1]
				
				if path == '/' :
					header = 'HTTP/1.1 200 OK'
					header += 'Connection: Close'
					header += 'Content-type: text/html; charset=utf-8\n\n'
					
					message = "<HTML><HEAD><TITLE>Historique</TITLE></HEAD><BODY><h1>History</h1>"
					history = open('history','r')
					for line in history :
						message += "\t<li>{}</li>\n".format(line.replace("<","&lt;").replace('>','&gt;'))
					history.close()
					message += '</BODY></HTML>'
					html = header + message
					clientweb.send(html.encode())
				else :
					header = 'HTTP/1.1 403 Forbidden'
					header += 'Connection: Close'
					header += 'Content-type: text/html; charset=utf-8 \n\n'
					message = "<HTML><HEAD><TITLE>Page introuvable</TITLE></HEAD><BODY><h1>403 Forbidden</h1></BODY></HTML>"
					html = header + message
					clientweb.send(html.encode())
				clientweb.shutdown(1)
				clientweb.close()
				
			if input == serveurSocket :
				
				client, info = connection.accept()
				#On recoit l'identifiant du client 
				clientName = client.recv(255).decode()
				
				newConnMsg = onConnMessage(clientName)
				addMessageHistory('history', newConnMsg+'\n')
				
				coloredNewConnMsg = colorString('green', newConnMsg)
				sysPrint(coloredNewConnMsg)
				#On ajoute le couple cle-valeur a notre dictionnaire
				selfMessage = "Bienvenue sur le serveur @localhost:{} {}".format(serverPort,clientName)
				client.send(colorString('green',selfMessage).encode())
				send2All(connectedUsers, coloredNewConnMsg)
				connectedUsers[client] = clientName
			
	try :
		messagesEntrants, wlist2, xlist2 = select.select(connectedUsers, [], [], 0.1)
	except select.error :
		 pass
	else :
		for socket in messagesEntrants :
			message = socket.recv(255).decode()
			
			#Socket est l'identifiant "machine", writerName est un id lisible pour l'Homme
			writerName = connectedUsers.get(socket)
			
			#DECONNEXION D'UN CLIENT
			if message.replace('\n', '') == '/exit' :
				deconnMsg = onDeconnMessage(writerName)
				addMessageHistory('history', deconnMsg + '\n')
				message = colorString('red',deconnMsg)
				socket.send('/exit'.encode())
				socket.close()
				del connectedUsers[socket]
			
			#CHANGEMENT de PSEUDO	
			elif message.split(' ')[0] == '/name' :
				newUserName = message.split(' ')[1].replace('\n', '')
				
				if newUserName not in connectedUsers.values():
					connectedUsers[socket] = newUserName
					
					newNameMsg = onChangeNameMsg(writerName, newUserName)
					addMessageHistory('history', newNameMsg + '\n')
					message = colorString('green', newNameMsg)
					
				else :
					socket.send(colorString('red' , 'Erreur, le pseudo {} n\'est pas disponible.'.format(newUserName)).encode())
					sysPrint(colorString('red', 'Changement de nom impossible {} -> {}'.format(writerName, newUserName)))
					continue #Echapement
					
			#MESSAGES PRIVEE
			elif message != '' and message[0] == "@" :
				
				# @foo toto -> ['@', 'foo toto\n'] -> ['foo', 'toto\n']
				destAndMessage = message.split('@')[1].split(' ', 1)
				
				destinataire = destAndMessage[0] 				# ['foo', 'toto'] -> 'foo'	
				message = destAndMessage[1].replace('\n', '') 	# ['foo', 'toto\n'] -> 'toto'
				
				#Test si le nom de l'utilisateur est connu
				if destinataire in connectedUsers.values() :
					#Obtention du socket associe a ce nom d'utilisateur
					socketDestinataire = getSocketFromName(connectedUsers, destinataire)
					
					#Message destine au serveur
					serverMsg = colorString('blue', "<{}@{}> : {}".format(writerName,destinataire,message))
					#Message destine aux deux clients
					message = colorString('blue', "<{}> : {}".format(writerName,message))
					
					#ENVOIE DU MP AU DESTINATAIRE PUIS A L'ENVOYEUR
					socketDestinataire.send(message.encode())
					socket.send(message.encode())
					sys.stdout.write(serverMsg)
					continue # Echapement pour ne pas afficher le message au reste des utilisateurs
					
				# Dans le cas ou l'utilisateur est inconnu, un message d'erreur est envoye au client
				else :
					errorMessage = "\033[31mErreur, client <{}> inconnu\033[0m\n".format(destinataire)
					socket.send(errorMessage.encode())
					sys.stdout.write(errorMessage)
					continue #Echapement pour ne pas afficher $message
			
			#MESSAGE "NORMAL"
			elif message != '' :
				message = "<{}> : {}".format(writerName, message)
				addMessageHistory('history', message)
	
			
			send2All(connectedUsers, message)
			sys.stdout.write(message)

