import socket as Socket
import time
import os
import re
from datetime import datetime

config = {
	"host" : "192.168.43.204", # HOST-ul serverului
	"port" : 5005 		   # PORT-ul pe care este mapat serverul
}

connectionParameters = (config["host"], config["port"])

# functie lambda de encodare a mesajului, din string in binar
data_encode = lambda message : message.encode("utf-8")

# functie lambda de decodare a mesajului, de la binar la string
data_decode = lambda message : message.decode("utf-8")

# functie care prelucreaza mesajul pentru a adauga informatii utile identificarii in logfile
def MessageInfos(message):
	print("* Se prelucreaza mesajul...")
	currentTime = datetime.now().strftime("%D->%H:%M:%S")
	message = f"[{currentTime}] {message}"
	time.sleep(0.5)
	print("* Mesajul a fost prelucrat cu succes...")
	return message


# functie care salveaza un mesaj intr-un "log" file
def LogInfo(message):
	# "a" : append
	with open("logfile.txt","a") as logfile:
		logfile.write(f"{message}\n")


if __name__ == "__main__":
	print("---------------------------------------------")
	# folosim with pentru inchiderea automata a socket-ului
	# AF-INET : familia de adrese IPv4
	# SOCK_STREAM : comunicare TCP
	with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as socket:
		# se realizeaza conectarea la server
		socket.connect(connectionParameters)
		print("* M-am conectat la server!")
		# bucla infinita de comunicare dintre client si server
		# flow aplicatie : clientul primeste mesaje de la server, le prelucreaza si le scrie intr-un logfile
		while True:
			print("\nAstept un mesaj...")
			# functie blocanta ce asteapta primirea a 1024 de octeti
			data = socket.recv(1024)

			# mesajul soseste in format binar, deci trebuie convertit la string
			message = data_decode(data)
			print(f"* A fost receptionat mesajul : {message}")

			# a fost receptionat mesajul de la server, urmeaza prelucrarea mesajului
			message = MessageInfos(message)

			# salvam fisierul in logfile
			LogInfo(message)

			# trimitem server-ului confirmare pentru primite si efectuarea sarcinii cu succes
			responseMessage = data_encode("OK")
			socket.sendall(responseMessage)
