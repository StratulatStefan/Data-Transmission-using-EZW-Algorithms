import socket
import serial
import time
import re
import subprocess
from handshake import *
from general_use import *
from communication import *

config = {
	"host" : "192.168.43.43", # HOST-ul serverului
	"port" : 7000 		  # PORT-ul pe care serverul asculta
}

# functie care identifica modalitatea de comunicare dorita, pe baza alegerii clientului
def GetCommunicationMode() -> int:
	while True:
		consoleDialog = "*********************************\n"
		consoleDialog += ">>> Selectati modalitatea de comunicare dorita\n"
		consoleDialog += ">>>\t[0] Comunicare prin socket-uri TCP\n"
		consoleDialog += ">>>\t[1] Comunicare prin UART\n"
		consoleDialog += ">>> Selectia dumneavoastra : "
		selection = int(input(consoleDialog))
		if selection < 0 or selection > 1:
			print(">>> Ati ales gresit! Mai incercati odata!")
		else:
			userselection = "UART" if selection == 1 else "Socket-uri TCP"
			print(f">>> Ati ales {userselection}!")
			print("*********************************")
			break
		print("*********************************")
	return selection


if __name__ == "__main__":
	# curatam consola pentru o afisare mai cool
	subprocess.call("clear", shell = True)
	print("-------------------------------------")
	# folosim with pentru inchiderea automata a socket-ului
	# AF-INET pentru familia de adrese IPv4
	# SOCK_STREAM pentru comunicare prin TCP
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		# setam posibilitatea de a refolosi o adresa deja folosita
		# pentru a preintampina o eroare care apare din cauza inchiderii fortate a conexiunii
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		# asocierea socket-uui cu o interfata specificare de retea si un port
		sock.bind((config["host"], config["port"]))
		# initiem ascultarea pentru clienti
		print("* Se asteapta clienti!")
		sock.listen()

		# asteptam conectarea unui client
		# apelam functia blocanta ce va returna conectiunea si adresa clientului
		connection, address = sock.accept()

		# clientul este conectat si putem incepe comunicarea
		with connection:
			print(f"* S-a conectat un client : {address}")
			# identificam modalitatea de comunicare
			communicationMode = GetCommunicationMode()
			# - bucla infinita pentru a repeta handshake-ul, ori de cate ori este nevoie
			# pana se efectueaza cu succes
			while True:
				# informam clientul cu privire la alegerea facuta si realizam handshake-ul
				# salvam status-ul handshake-ului, conexiunea si tipul conexiunii
				type, conn, HSstatus = CommunicationHandshake(connection, communicationMode)
				if not HSstatus:
					# handshake esuat
					print("* Handshake-ul a esuat!")
					print("* Se reia handshake-ul!")
				else:
					# handshake efectuat cu succes
					if type == 0:
						# initiem comunicarea prin TCP
						# parasim bucla de reluare a handshake-ului, deoarece a fost efectuat cu succes
						TCPCommunication(conn)
						break
					elif type == 1:
						# initiem comunicarea prin UART
						# parasim bucla de reluare a handshake-ului
						UARTCommunication(conn)
						break
					else:
						# tipul de comunicare identificat este eronat
						# reluam handshake-ul
						print("* Canal de comunicare ales eronat!")

