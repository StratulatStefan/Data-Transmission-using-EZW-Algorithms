import socket
import serial
import subprocess
from general_use import *
from handshake import *

config = {
	"host" : "192.168.43.43", # HOST-ul serverului
	"port" : 7000		  # PORT-ul pe care este mapat serverul
}

def TCPCommunication(connection):
	print("FUCK YEAH")
	exit(0)

def UARTCommunication(connection):
	pass



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
			# functie blocanta care citeste 1024 de octeti de pe canalul de comunicare
			data = sock.recv(1024)

			# verificam daca se doreste realizarea Handshake-ului
			decoded_data = data_decode(data)
			print(f"* Am primit mesajul : {decoded_data}!")

			if "[HS]" in decoded_data:
				# se realizeaza Handshake-ul
				type, connection, handshake_state = CommunicationHandshake(sock, decoded_data)
				if not handshake_state :
					# handshake esuat
					print("* Handshake-ul a esuat!")
					exit(-1)
				else:
					if type == 0:
						TCPCommunication(connection)
					elif type == 1:
						UARTCommunication(connection)
					else:
						print("dafuk!")
						exit(-1)
