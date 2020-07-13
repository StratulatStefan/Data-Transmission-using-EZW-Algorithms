import socket as Socket
import time

config = {
	"host" : "192.168.43.204", # HOST-ul serverului
	"port" : 5005              # PORT-ul pe care serverul va asculta
}

connectionParameters = (config["host"], config["port"])

# functie lambda care transforma un mesaj din format binar in format string
data_decode = lambda message : message.decode("utf-8")

# functie lambda care transforma un mesaj din format string in format binar
data_encode = lambda message : message.encode("utf-8")


# functie care verifica daca ack-ul primit este corect
# ack corect : "OK"
def CheckACK(ackMessage):
	if "OK" in ackMessage:
		return True
	return False


if __name__ == "__main__":
	print("------------------------------------------")
	# folosim with pentru inchiderea automata a socket-ului
	# AF_INET : familia de adrese IPv4
	# SOCK_STREAM : comunicare TCP
	with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as socket:
		# asocierea socket-ului cu o interfata specifica de retea si un port
		socket.bind(connectionParameters)
		print("* Se asteapta clienti!")
		# initiem ascultarea pentru clienti
		socket.listen()

		# asteptam pana cand un client se conecteaza
		# functia accept este blocanta si returneaza conexiunea si adresa clientului
		connection, address = socket.accept()

		with connection:
			print(f"* S-a conectat un client : ", end="") 
			print(f"[Adresa IP] {address[0]}", end="")
			print(f"  [Port] {address[1]}\n")
			# serverul citeste mesaje de la tastatura, pe care clientul le salveaza intr-un logfile
			while True:
				# citim un mesaj de la tastatura
				message = input("\n* Introduceti mesajul : ")

				# eliminam caracterele redundante
				message = message.strip("\r\n")

				# datele circula prin canalele de comunicatie in format binar
				# facem conversia mesajului de la string la binar
				data = data_encode(message)

				# trimitem mesajul catre client
				connection.sendall(data)

				# asteptam primirea raspunsului de la client
				# folosim o functie blocanta, astfel nu putem trimite alt mesaj pana nu primim confirmare
				ack = connection.recv(1024)

				# decodam mesajul primit si verificam daca este cel corect
				# in caz contrar, oprim conexiunea
				ackdata = data_decode(ack)
				if CheckACK(ackdata):
					print("* Mesajul a fost trimis si inregistrat cu succes!")
					continue
				else:
					break

