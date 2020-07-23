from general_use import *
import time
import sys
import os
import re

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


# functia care realizeaza transmiterea fisierelor prin UART
def UARTCommunication(connection):
	while True:
		filename = input("Introduceti numele fisierului: ")
		filename = filename.strip("\r\n")
		print(f"* Numele fisierului : {filename}")
		
		# trimitem numele fisierului pe portul serial
		encoded_filename = data_encode("[nume] " + filename)
		bytes_count = connection.write(encoded_filename)
		print(f"[Am trimis \"{filename}\" [{bytes_count} octeti] pe portul serial!]")
		time.sleep(0.25)

		# citim imaginea in format binar si trimitem continutul pe portul serial
		for imageBitStream in FileBinaryRead(filename):
			bytes_count = connection.write(imageBitStream)
			print(f"[Am trimis {bytes_count} octeti pe portul serial!]")
		print("\n")
		print(f"[Fisierul a fost trimis cu succes!]")


# functia care realizeaza transmiterea fisierelor prin TCP
def TCPCommunication(connection):
	print("--------------------------------------")
	with connection:
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
			socketWRITE(connection, filename_tosend)
			time.sleep(0.25)

			# trimitem continutul fisierului sub forma de pachete de octeti
			# pachete de octeti sunt generate secvential, pe masura ce se citeste fisierul
			for packet in FileBinaryRead(filename):
				socketWRITE(connection, packet)
				print("* S-a trimis un pachet de {PACKET_SIZE} octeti.")
			print("************************************")
			print("Fisierul a fost trimis cu succes!")
			print("************************************\n\n")