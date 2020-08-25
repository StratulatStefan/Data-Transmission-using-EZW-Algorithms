from communication.general_use import *
import re
import os
import time
import sys

# functie care verifica daca mesajul primit reprezinta numele fisierului
# numele fisierului se identifica astfel : [nume] <nume_fisier>.<extensie>
# numele fisierului nu poate fi identificat daca:
# 1). nu contine [nume]
# 2). primim exceptie din cauza imposibilitatii de a decoda octetii la codec-ul utf-8
def CheckForFilename(content):
	try:
		data = data_decode(content)
		print(data)
		if "[nume]" in data:
			return True
	except UnicodeDecodeError:
		pass
	return False

# functie care extrage numele fisierului din mesajul primit
def ExtractFileName(content):
	pattern = "\s.+"
	matches = re.findall(pattern, content)
	return matches[0][1:]

# functie care verifica daca fisierul pe care dorim sa il scriem exista
def CheckForExistanceAndDelete(filename):
	if os.path.exists(filename):
		# -fisierul exista pe disc, deci trebuie sters, deoarece 
		# scrierea in fisier se face secvential, folosind "ab" (append binary)
		os.remove(filename)

# functia care realizeaza transmiterea fisierelor prin TCP
def TCPCommunication(connection):
	print("-------------------------------")
	with connection:
		# bucla infinita pentru receptia de pachete de octeti
		while True:
			print("***********************")
			print("Waiting for data...")
			# asteptam (blocant) receptionarea a 1024 de octeti
			data = socketREAD(connection)

			# verificam daca am primit numele fisierului
			if CheckForFilename(data):
				# am primit numele fisierului
				# facem conversia la string si salvam numele fisierului
				fname = data_decode(data)
				filename = ExtractFileName(fname)
				print(f"* Am primit numele fisierului : {filename}!")
				CheckForExistanceAndDelete(filename)
				time.sleep(0.25)
			else:
				# am primit un pachet de octeti din continutul fisierului
				print("* Am primit un pachet de date!")

				# folosim "ab" (append binary) deoarece scrierea fisierului
				# se face secvential, la fiecare iteratie a buclei while (cu fiecare pachet primit)
				# este mai eficient decat a pastra fisierul in memorie si a-l scrie la final
				with open(filename, "ab") as file:
					file.write(data)


# functia care realizeaza transmiterea fisierelor prin UART
def UARTCommunication(connection):
	# bucla infinita pentru asteptarea de pachete de octeti
	while True:
		print("----------------------------------------")
		print("[Waiting for data]")

		# citim un octet de pe portul serial
		data_chunk = connection.read()
		time.sleep(0.01)

		# identificam si citim restul octetilor de pe portul serial
		remaining_bytes = connection.inWaiting()
		data_chunk += connection.read(remaining_bytes)

		# - verificam daca mesajul primit reprezinta numele fisierului
		# sau un pachet de octeti ce compun fisierului
		if CheckForFilename(data_chunk):
			data_chunk = data_decode(data_chunk)
			filename = ExtractFileName(data_chunk)
			print(f"[Am primit numele fisierului : \"{filename}\"]")
			CheckForExistanceAndDelete(filename)
			time.sleep(0.1)
		else:
			# primim pachete de octeti care compun fisierul
			print(f"[Am primit {remaining_bytes + 1} octeti pe portul serial.]")
			# folosim with pentru inchiderea automata a fisierului
			# - folosim "ab" (append binary), deoarece scrierea fisierului
			# se face secvential, la fiecare iteratie a buclei while
			# -nu dorim sa pastram fisierul in memorie si sa il scriem la final
			# dorim sa scriem fisierul pe masura ce primim octetii
			with open(filename, "ab") as file:
				file.write(data_chunk)
		#	pass
