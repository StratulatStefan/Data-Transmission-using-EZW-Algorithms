import socket
import serial
import subprocess
from general_use import *
from handshake import *

config = {
	"host" : "192.168.43.43", # HOST-ul serverului
	"port" : 7000		  # PORT-ul pe care este mapat serverul
}

# functia care realizeaza transmiterea fisierelor prin TCP
def TCPCommunication(connection):
	print("FUCK YEAH")
	exit(0)

# functia care realizeaza transmiterea fisierelor prin UART
def UARTCommunication(connection):
	print("FUCK YEAHsss")
	exit(0)



if __name__ == "__main__":
	# curatam consola pentru o afisare mai buna
	subprocess.call("clear", shell = True)
	print("-------------------------------------------------")
	# folosim with pentru inchiderea automata a socket-ului
        # AF-INET pentru familia de adrese IPv4
        # SOCK_STREAM pentru comunicare prin TCP
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		# se realizeaza conectarea la server
		sock.connect((config["host"], config["port"]))
		print("* M-am conectat la server!")

		# bucla infinita de comunicare dintre server si client
		while True:
			# asteptam primirea unui mesaj pe socket
			decoded_data = socketREADMessage(sock)
			print(f"* Am primit mesajul : {decoded_data}!")

			if "[HS]" not in decoded_data:
				# aceasta secventa se ocupa doar de realizeaza handshake-ului
				# un mesaj care cu contine identificatorul de handshake este un mesaj eronat
				# transmitem un mesaj de eroare!
				errorMessage = "Waiting for handshake!"
				socketWRITEMessage(sock, errorMessage)
			else:
				# se realizeaza Handshake-ul
				type, connection, handshake_state = CommunicationHandshake(sock, decoded_data)
				if not handshake_state :
					# handshake esuat
					print("* Handshake-ul a esuat!")
					# informam serverul ca handshake-ul a esuat!
					errorMessage = "Handshake error!"
					socketWRITEMessage(sock, errorMessage)
					# - astfel, asteptam reincercarea executiei handshake-ului la urmatoarea 
					# parcurgere a buclei 
				else:
					# handshake efectuat cu succes
					if type == 0:
						# initiem comunicarea prin TCP
						TCPCommunication(connection)
					elif type == 1:
						# initiem comunicarea prin UART
						UARTCommunication(connection)
					else:
						# am primit un tip eronat de comunicare
						print("* Canal de comunicare ales eronat!")
						# asteptam reluarea handshake-ului si primirea unui tip valid
