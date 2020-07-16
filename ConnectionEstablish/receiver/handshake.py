from general_use import *
import serial

# functie care trateaza realizarea handshake-ului cu serverul
def CommunicationHandshake(sock, data) -> bool:
	print("******************")
	ErrorResponse = None, None, False
	print("Handshake\n")
	# verificam daca initializarea Handshake-ului contine "INIT"; altfel, intrerupem
	if "INIT" not in data:
		pass
		#return ErrorResponse
	# identificam tipul de comunicare dorita : 0 - TCP | 1 - UART
	comtypeId = communication_type(data)
	comtypeName = "TCP" if comtypeId == 0 else "UART" if comtypeId == 1 else None
	print(f"* Modalitate de comunicare aleasa : {comtypeName}")
	print(f"* Trimitem ACK catre server...")
	# formam mesajul de ACK si il trimitem catre server
	ackmessage = f"[HS] STARTED {comtypeName}"
	encodedack_message = data_encode(ackmessage)
	sock.sendall(encodedack_message)
	print(f">>> ACK trimis cu succes catre server!")

	# incepem secventa de trimitere de mesaje de verificare pe canalul de comunicare stabilit
	print(f"* Incepem secventa de verificare specifica {comtypeName}...")
	connection = None
	if comtypeId == 0 :
		connection = sock
	elif comtypeId == 1:
		connection = serial.Serial("/dev/ttyS0", baudrate = 576000, timeout=None)

	invalidcomtypeId = comtypeId < 0 or comtypeId > 1
	if invalidcomtypeId or not ConnectionCheck(connection, comtypeId):
		return ErrorResponse

	return comtypeId, connection, True
	print("******************\n\n")

# functia care trimite mesaje de verificare a conexiunii, corespunzator mediului de comunicare ales
def ConnectionCheck(connection, selection) -> bool:
	# determinam functiile necesare pentru citire si scriere, pe baza tipul de comunicare ales
	# folosim referinte la acele functii
	readFunction = uartREADMessage if selection == 1 else socketREADMessage if selection == 0 else None
	writeFunction = uartWRITEMessage if selection == 1 else socketWRITEMessage if selection == 0 else None

	print("\n\n")
	# ne asteptam sa primim 3 mesaje
	messages_count = 1
	while True:
		# asteptam primirea unui mesaj
		print("* Asteptam mesajul...")
		data = readFunction(connection)
		# extragem doar continutul relevant
		if "[HS]" not in data:
			pass
		decoded_data = relevant_data_handshake(data)
		print(f">>> Am primit mesajul {decoded_data}")
 		# extragem indexul verificarii din mesaj
		id = int(extract_number(decoded_data))
		if id > messages_count:
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
				break
	print(f"* Handshake realizat cu succes!")
	return True

