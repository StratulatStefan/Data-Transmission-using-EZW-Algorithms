import socket as Socket
import os
import time
import re

config = {
	"host" : "192.168.43.204",  # HOST-ul serverului
	"port" : 5005   	    # PORT-ul pe care este mapat serverul
}

connectionParameters = (config["host"], config["port"])

# functie globala care va contine numele fisierului de scris
filename = None

# functie lambda care decodeaza mesajul, din binar in string
# folosita doar in cadrul decodarii numelui fisierului
data_decode = lambda message : message.decode("utf-8")


# functie care verifica daca continutul primit reprezinta numele fisierului
# nu am primit numele fisierului daca
#	1). nu contine [nume]
# 	2). nu putem face conversia cu codec utf-8 la string de la binar
def ReceivedFileName(data):
	try:
		filename = data_decode(data)
		if "[nume]" in filename:
			return True
	except UnicodeDecodeError:
		pass
	return False

# functie care extrage numele fisierului din mesajul primit
def ExtractFileName(data):
	pattern = "\s.+"
	matches = re.findall(pattern,data)
	return matches[0][1:]

# functie care verifica daca fisierul exista si il sterge
# deoarece se face append (scriere secventiala)
def CheckFileAndDelete(filename):
	if os.path.exists(filename):
		os.remove(filename)

if __name__ == "__main__":
	print("-------------------------------")

	# folosim with pentru inchiderea automata socket-ului
	# AF-INET : familia de adrese IPv4
	# SOCK_STREAM : comunicare TCP
	with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as socket:
		# se realizeaza conectarea la server
		socket.connect(connectionParameters)
		print("* M-am conectat la server!")

		# bucla infinita pentru receptia de pachete de octeti
		while True:
			print("***********************")
			print("Waiting for data...")
			# asteptam (blocant) receptionarea a 1024 de octeti
			data = socket.recv(1024)

			# verificam daca am primit numele fisierului
			if ReceivedFileName(data):
				# am primit numele fisierului
				# facem conversia la string si salvam numele fisierului
				fname = data_decode(data)
				filename = ExtractFileName(fname)
				print(f"* Am primit numele fisierului : {filename}!")
				CheckFileAndDelete(filename)
				time.sleep(0.25)
			else:
				# am primit un pachet de octeti din continutul fisierului
				print("* Am primit un pachet de date!")

				# folosim "ab" (append binary) deoarece scrierea fisierului
				# se face secvential, la fiecare iteratie a buclei while (cu fiecare pachet primit)
				# este mai eficient decat a pastra fisierul in memorie si a-l scrie la final
				with open(filename, "ab") as file:
					file.write(data)


