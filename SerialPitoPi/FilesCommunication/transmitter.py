import serial
import time
import sys

# definim si initializam portul serial pentru transmiterea datelor
port = serial.Serial("/dev/ttyS0", baudrate=576000)

# functia care citeste un fisier (in cazul nostru, o imagine) si ii returneaza
# continutul in format binar
def ImageBinaryRead(filename):
	# rb : read binary
	# folosim with pt. inchiderea automata a fisierului
	# - citim cate block_size octeti din fisier si folosim un generator (yield)
	# pentru a furniza un pachet care sa fie trimis
	# - asadar, trimitea fisierului se face secvential, prin descompunerea fisierului
	# in cate block_size pachete si trimiterea fiecaruia pe rand
	block_size = 512
	with open(filename, "rb") as file:
		while True:
			bytes = file.read(block_size)
			if not bytes:
				break
			yield bytes

# functia lambda care codifica un string in format binar
data_encode = lambda message : message.encode("utf-8")

if __name__ == "__main__":
	print("----------------------------------------")

	# numele fisierului va fi furnizat ca argument la linia de comanda
	# asadar, verificam sa avem numarul corect de argumente furnizate
	# avem nevoie 2 argumente (numele scriptului si numele fisierului)
	# daca numarul nu este corect, oprim executia programului
	arguments_count = len(sys.argv)
	if arguments_count != 2:
		print("Furnizati numele fisierului!")
		exit(-1)
	image_filename = sys.argv[1]
	print(f"Numele fisierului : {image_filename}")

	'''
	-  pentru ca receiver-ul sa poata scrie fisierul pe disc, acesta are nevoie 
	de continutul fisierului si de numele acesteia; chiar daca numele fisierului este
	codificat in headerele corespunzatoare fisierului, nu ne complicam sa il cautam 
	acum, ci vom trimite mai intai numele fisierului, si apoi continutul
	[nume] <nume_fisier>.<extensie>
	<continut>
	'''

	# trimitem numele fisierului pe portul serial
	encoded_filename = data_encode("[nume] " + image_filename)
	bytes_count = port.write(encoded_filename)
	print(f"[Am trimis \"{image_filename}\" [{bytes_count} octeti] pe portul serial!]")
	time.sleep(0.25)

	# citim imaginea in format binar si trimitem continutul pe portul serial
	for imageBitStream in ImageBinaryRead(image_filename):
		bytes_count = port.write(imageBitStream)
		print(f"[Am trimis {bytes_count} octeti pe portul serial!]")
	print("\n")
	print(f"[Fisierul a fost trimis cu succes!]")

