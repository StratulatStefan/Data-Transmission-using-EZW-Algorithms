import socket as Socket
import time
import sys

config = {
	"host" : "192.168.43.204", # HOST-ul serverului
	"port" : 5005  		   # PORT-ul pe care serverul asculta
}

connectionParameters = (config["host"], config["port"])

# functie lambda care de encodare a mesajului, din string in binar
# folosita doar in cadrul encodarii numelui fisierului
data_encode = lambda message : message.encode("utf-8")

# dimensiunea pachetului trimis prin socket
# dimensiunea pachetului citit din fisier
PACKET_SIZE = 1024

# functie care formateaza numele fisierului, astfel incat sa satisfaca conventia
# stabilita si sa poate fi trimis prin canalul de comunicatie
def FormatFileName(filename):
	# adaugare prefix
	filename = f"[nume] {filename}"

	# convertire la binar
	return data_encode(filename)

# functie care citeste secvential un fisier, in pachete de cate PACKET_SIZE octeti, pe care le genereaza pentru a fi trimise
def FileBinaryRead(filename):
	# rb : read binary
	# folosim with pt inchiderea automata a fisierului
	with open(filename, "rb") as file:
		while True:
			bytes = file.read(PACKET_SIZE)
			if not bytes:
				break
			yield bytes

if __name__ == "__main__":
	print("--------------------------------------")

	# folosim with pentru inchiderea automata a socket-ului
	# AF-INET : familia de adrese IPv4
	# SOCK_STREAM : comunicare TCP
	with Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) as socket:
		# asocierea socket-ului cu o interfata specifica si un port
		socket.bind(connectionParameters)
		print("* Se asteapta clienti!")

		# initiem ascultarea pentru clienti
		socket.listen()

		# asteptam pana cand un client se conecteaza
		# functia accept este blocanta si returneaza conexiunea si adresa clientului
		connection, address = socket.accept()

		with connection:
			print(f"*S-a conectat un client : ", end="")
			print(f"[Adresa IP] {address[0]}  ", end="")
			print(f"[Port] {address[1]}\n")
			while True:
				filename = input("Introduceti numele fisierului : ")
				filename = filename.strip("\r\n")
				print(f"* Numele fisierului : {filename}")
				'''
				- Pentru a putea trimite un fisier si pentru a-l salva la receptie, avem nevoie de continutul acestuia si de continut
				- Cu toate ca avem numele fisierului encodat in headerele fisierului, il vom trimite explicit.
				- Astfel, prima data trimitem numele fisierului in format [nume] <nume>.<extensie> si apoi trimitem continutul sub 
				forma de pachete de octeti.
				'''

				# trimitem fisierului (primit ca argument la cmd) catre receptor
				filename_tosend = FormatFileName(filename)
				print(f"* Trimitem numele fisierului [{filename}]!")
				connection.sendall(filename_tosend)
				time.sleep(0.25)

				# trimitem continutul fisierului sub forma de pachete de octeti
				# pachete de octeti sunt generate secvential, pe masura ce se citeste fisierul
				for packet in FileBinaryRead(filename):
					connection.sendall(packet)
					print("* S-a trimis un pachet de {PACKET_SIZE} octeti.")
				print("************************************")
				print("Fisierul a fost trimis cu succes!")
				print("************************************\n\n")

