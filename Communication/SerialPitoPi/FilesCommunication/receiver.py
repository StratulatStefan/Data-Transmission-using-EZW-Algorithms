import serial
import time
import re
import os

# definim si initializam portul serial pentru transmiterea datelor
# setam timeout=None pentru a astepta la infinit mesaj
port = serial.Serial("/dev/ttyS0", baudrate=576000, timeout=None)

# variabila globala ce va identifica numele fisierului a carui continut va fi receptionat
filename = None

# functie lambda care se ocupa de decodarea, in format string, a mesajului primit
# functia este folosita doar in cazul primirii numelui imaginii
data_decode = lambda message : message.decode("utf-8")

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


if __name__ == "__main__":
	# bucla infinita pentru asteptarea de pachete de octeti
	while True:
		print("----------------------------------------")
		print("[Waiting for data]")

		# citim un octet de pe portul serial
		data_chunk = port.read()
		time.sleep(0.01)

		# identificam si citim restul octetilor de pe portul serial
		remaining_bytes = port.inWaiting()
		data_chunk += port.read(remaining_bytes)

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
