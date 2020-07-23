from general_use import *
import serial

# functie care trateaza realizarea handshake-ului cu serverul
# se asteapta primirea mesajului de initializare a Handshake-ului
def CommunicationHandshake(sock, data) -> bool:
	print("******************")
	# raspuns returnat in cazul in care handshake-ul a esuat
	ErrorResponse = None, None, False
	print("Handshake\n")
	# verificam daca initializarea Handshake-ului contine "INIT"; altfel, intrerupem
	reloads = 1
	while True:
		if "INIT" not in data:
			if reloads == 3:
				# se permit doar 3 erori! Returnam eroare!
				return ErrorResponse
			# nu am primit un mesaj valid! Atentionam serverul!
			errorMessage = "Waiting for handshake!"
			socketWRITEMessage(sock, errorMessage)
			reloads += 1
			time.sleep(1)
			continue
		else:
			reloads = 1
			break

	# identificam tipul de comunicare dorita : 0 - TCP | 1 - UART
	comtypeId = communication_type(data)
	comtypeName = "TCP" if comtypeId == 0 else "UART" if comtypeId == 1 else None
	print(f"* Modalitate de comunicare aleasa : {comtypeName}")
	print(f"* Trimitem ACK catre server...")
	# formam mesajul de ACK si il trimitem catre server
	ackmessage = f"[HS] STARTED {comtypeName}"
	socketWRITEMessage(sock, ackmessage)
	print(f">>> ACK trimis cu succes catre server!")

	# incepem secventa de trimitere de mesaje de verificare pe canalul de comunicare stabilit
	print(f"* Incepem secventa de verificare specifica {comtypeName}...")
	# determinam comunicarea necesara, pe baza tipului de comunicare
	connection = None
	if comtypeId == 0 :
		# folosim socket-ul pe care l-am primit ca parametru
		connection = sock
	elif comtypeId == 1:
		# definim un port serial pentru transmiterea datelor
		# portul pe care se va mapa UART : /dev/ttyS0
		# nr. de biti trimiti pe secunda : baudrate
		# functia de citire a datelor asteapta primirea datelor la infinit : timeout = None
		connection = serial.Serial("/dev/ttyS0", baudrate = 576000, timeout=None)
	# valoare booleana ce devine True, daca tipul de comunicare stabilit este invalid
	invalidcomtypeId = comtypeId < 0 or comtypeId > 1
	# apelam functia de transmitere a mesajelor de verificare, corespunzatoare comunicarii alese
	if invalidcomtypeId or not ConnectionCheck(connection, comtypeId):
		# nu avem tipul de comunicare dorit sau transmiterea de mesaje intre medii a esuat
		return ErrorResponse

	# - comunicarea dintre cele doua medii s-a efectuat cu succes, deci handshake-ul s-a efectuat cu succes
	# comunicarea poate fi stabilita
	return comtypeId, connection, True
	print("******************\n\n")

# functia care trimite mesaje de verificare a conexiunii, corespunzator mediului de comunicare ales
def ConnectionCheck(connection, selection) -> bool:
	# determinam functiile necesare pentru citire si scriere, pe baza tipul de comunicare ales
	# folosim referinte la acele functii
	readFunction = uartREADMessage if selection == 1 else socketREADMessage if selection == 0 else None
	writeFunction = uartWRITEMessage if selection == 1 else socketWRITEMessage if selection == 0 else None

	print("\n\n")
	# ne asteptam sa primim 3 mesaje, pentru care trebuie sa trimitem confirmare
	# fiecare mesaj trebuie sa aiba un index specific, mai mic/egal cu 3
	messages_count = 1
	while True:
		# asteptam primirea unui mesaj
		print("* Asteptam mesajul...")
		data = readFunction(connection)
		if "[HS]" not in data:
			# nu primim un mesaj specific handshake-ului
			pass
		# pastram informatia relevanta din mesaj
		decoded_data = relevant_data_handshake(data)
		print(f">>> Am primit mesajul {decoded_data}")
 		# extragem indexul verificarii din mesaj
		id = int(extract_number(decoded_data))
		if id > messages_count:
			# nu am primit mesajul cu indexul corect
			break
		#	pass
		elif id == messages_count:
			messages_count += 1
            		# am primit mesajul corect
            		# compunem mesajul de confirmare
			ack = f"[HS] ACK MSG{id}"
            		# trimitem confirmare
			print(f"* Trimitem mesajul de confirmare pentru MSG{id}")
			writeFunction(connection, ack)
			print(f">>> Am trimis confirmare pentru MSG{id}!")
			if id == 3:
				# am primit cele trei mesaje, deci handshake-ul a fost efectuat cu succes!
				break
	print(f"* Handshake realizat cu succes!")
	return True

