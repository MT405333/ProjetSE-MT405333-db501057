gnome-terminal -x python3 -x server.py 8888 8080
gnome-terminal -x python3 client.py localhost 8888 client1
gnome-terminal -x python3 client.py localhost 8888 client2
firefox localhost:8080/toto
