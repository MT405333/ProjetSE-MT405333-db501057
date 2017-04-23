# lancer le serveur sur port 8888
# connecter pseudo client au serveur et envoyer « client »
rm result & rm expected
python3 server.py 8888 &
xterm -e sh -c 'printf client | netcat -w 1 localhost 8888 > result'

# mettre le resultat attendu dans le fichier expected
echo "\033[92mBienvenue sur le serveur @localhost:8888 client\033[0m" > expected
# comparer le resultat obtenu et le resultat attendu
diff result expected
# si aucune difference, le test est réussi
if [ $? -eq 0 ]
    then
        printf "[\033[92mPASS\033[0m] Test de connexion d'un client\n"
       
    else
        printf "[\033[31mFAIL\033[0m] Test de connexion d'un client\n"
fi
