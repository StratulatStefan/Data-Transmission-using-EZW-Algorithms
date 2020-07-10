import serial
import time
import subprocess

# initializam un port
# setm portul serial corespunzator
# setam nr. de biti trimisi per secunda=115200 (14 Kb)
# setam timeout, necesar la read (None : asteapta la infinit, pana cand se primeste ceva)
port = serial.Serial("/dev/ttyS0", baudrate=115200,timeout=None)

# functie lambda care se ocupa de decodarea, in format string, a mesajului primit.
data_decode = lambda message : message.decode("utf-8")

# realizam o bucla infinita pentru primirea datelor
while True:
#	subprocess.run("clear", shell=True)
	print("--------------------------------------------")
	print("[Waiting for data...]")
	# citim un octet de pe portul serial
	data_chunk = port.read()
	time.sleep(0.1)

	'''
	- functia de citire primeste ca parametru nr. de octeti pe care sa ii citeasca, 
	insa aceasta nu cunoaste cati octeti o sa citeasca
	- asadar, apelam mai intai functia implicita, care va citi 1 octeti
	- apoi apelam metoda inWaiting(), care va returna nr. de octeti ramasi in
	buffer-ul de intrare
	- furnizam aceasta valoare ca param. pt. functia read, care va sti astfel cati
	octeti sa citeasca
	- astfel, vom citi intreg mesajul trimis de transmitter
	'''
	remaining_bytes = port.inWaiting()
	data_chunk += port.read(remaining_bytes)
	data_chunk = data_decode(data_chunk)
	print(f"[Am citit {remaining_bytes + 1} octeti de pe portul serial.]")
	print(f"Mesajul primit : {data_chunk}")
	print("\n")
