import serial
import time
import subprocess

# initializam un port
# setam portul serial corespunzator
# setam nr. de biti trimisi per secunda = 115200 (14.400 octeti = 14 Kb)
port =  serial.Serial("/dev/ttyS0", baudrate=115200)

# functie lambda care codifica un string in format binar
data_encode = lambda message : message.encode("utf-8")
# eliminarea caractelor "new line" dintr-un string
data_format = lambda message : message.strip("\r\n")

while True:
	# stergem consola la fiecare nou loop pentru o afisare mai lizibila
	# folosim subprocess pentru a apela comanda "clear" din shell
	# subprocess.run("clear", shell=True)
	print("---------------------------------------------------------------------")

	# citim datele utilizatorului, eliminam "\n" si transformam in format binar
	user_data = input("Introduceti textul : ")
	user_data = data_format(user_data)
	user_data = data_encode(user_data)

	# trimitem mesajul pe portul serial si salvam nr. de biti transmisi
	print("\n[Incercam sa trimitem mesajul]")
	bytes_count = port.write(user_data)
	time.sleep(1)
	print(f"[Au fost trimis cu succes {bytes_count} octeti.]")
	print("\n")

