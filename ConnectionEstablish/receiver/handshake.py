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
	if comtypeId == 0 :
		if not TCPConnectionCheck(sock):
			return ErrorResponse
		return 0, sock, True
	elif comtypeId == 1:
		UARTConnection = serial.Serial("/dev/ttyS0", baudrate = 576000, timeout=None)
		if not UARTConnectionCheck(UARTConnection):
			return ErrorResponse
		return 1, UARTConnection, True
	else:
		return ErrorResponse
	print("******************\n\n")

def UARTConnectionCheck(port) -> bool:
	print("\n\n")
	# ne asteptam sa primim 3 mesaje
	messages_count = 1
	while True:
		# asteptam primirea unui mesaj
		print("* Asteptam mesajul...")
		data = port.read()
		remaining_bytes = port.inWaiting()
		data += port.read(remaining_bytes)
		# am primit un mesaj, pe care il decodificam
		decoded_data = data_decode(data)
		# extragem doar continutul relevant
		if "[HS]" not in decoded_data:
			pass
		decoded_data = relevant_data_handshake(decoded_data)
		print(f">>> Am primit mesajul {decoded_data}")
        # extragem indexul verificarii din mesaj
		id = int(extract_number(decoded_data))
		if id > messages_count:
			break
#              pass
		elif id == messages_count:
			messages_count += 1
            # am primit mesajul corect
            # compunem mesajul de confirmare
			ack = f"[HS] ACK MSG{id}"
            # encodam mesajul de confirmare
			encoded_ack = data_encode(ack)
            # trimitem confirmare
			print(f"* Trimitem mesajul de confirmare pentru MSG{id}")
			port.write(encoded_ack)
			print(f">>> Am trimis confirmare pentru MSG{id}!")
			if id == 3:
				break   
	print(f"* Handshake realizat cu succes!")
	return True


# functia care trimite mesaje de verificare a conexiunii prin Socket-uri TCP
def TCPConnectionCheck(sock) -> bool:
	print("\n\n")
	# ne asteptam sa primim 3 mesaje
	messages_count = 1
	while True:
		# asteptam primirea unui mesaj
		print("* Asteptam mesajul...")
		data = sock.recv(1024)
		# am primit un mesaj, pe care il decodificam
		decoded_data = data_decode(data)
		# extragem doar continutul relevant
		if "[HS]" not in decoded_data:
			pass
		decoded_data = relevant_data_handshake(decoded_data)
		print(f">>> Am primit mesajul {decoded_data}")
		# extragem indexul verificarii din mesaj
		id = int(extract_number(decoded_data))
		if id > messages_count:
			break
#			pass
		elif id == messages_count:
			messages_count += 1
			# am primit mesajul corect
			# compunem mesajul de confirmare
			ack = f"[HS] ACK MSG{id}"
			# encodam mesajul de confirmare
			encoded_ack = data_encode(ack)
			# trimitem confirmare
			print(f"* Trimitem mesajul de confirmare pentru MSG{id}")
			sock.sendall(encoded_ack)
			print(f">>> Am trimis confirmare pentru MSG{id}!")
			if id == 3:
				break
	print(f"* Handshake realizat cu succes!")
	return True
