from general_use import *
import time
import serial


# - functie care realizeaza handshake-ul cu clientul pentru a-l informa cu privire la modalitatea de comunicare
# aleasa si pentru a stabili conexiunea cu acesta
def CommunicationHandshake(TCPConnection, comselection) -> bool:
	print("**********************************")
	ErrorResponse = None, None, False
	print("Handshake\n")
	# identificam modalitatea de comunicare
	communication = "UART" if comselection == 1 else "TCP" if comselection == 0 else None
	# formam mesajul de initializare a Handshake-ului
	initMessage = f"[HS] INIT {communication}"
	# codificam mesajul
	initmsg = data_encode(initMessage)
	# trimitem mesajul catre client prin canalul de comunicare
	print("* Trimitem initializarea catre client!")
	TCPConnection.sendall(initmsg)
	print(">>> Initializare trimisa cu succes!")
	print("* Asteptam ACK de la client!")
	# asteptam primirea ack-ului de la client, pentru a indica daca a salvat modalitatea de comunicare
	ack = TCPConnection.recv(1024)
	ackdata = data_decode(ack)
	print(f">>> Am primit ACK de la client : {ackdata}!")
	if "STARTED" not in ackdata :
		pass
		# return ErrorResponse
	# incepem secventa de trimitere de mesaje de verificare pe canalul de comunicare stabilit
	print(f"* Incepem secventa de verificare specifica {communication}...")
	if comselection == 0:
		if not TCPConnectionCheck(TCPConnection):
			return ErrorResponse
		return 0, TCPConnection, True
	elif comselection == 1:
		UARTConnection = serial.Serial("/dev/ttyS0", baudrate = 576000, timeout=None)
		if not UARTConnectionCheck(UARTConnection):
			return ErrorResponse
		return 1, UARTConnection, True
	else:
		return ErrorResponse

	print("**********************************\n\n")

# functia care trimite mesaje de verificare a conexiunii prin Socket-uri TCP
def TCPConnectionCheck(sock) -> bool:
	print("\n\n")
	# vom trimite 3 mesaje pentru care asteptam confirmare imediata
	for index in range(1,4):
		# compunem mesajul
		verification_msg = f"[HS] MSG{index}"
		# encodam mesajul
		encoded_verification_msg = data_encode(verification_msg)
		# trimitem mesajul
		print(f"* Am trimis MSG{index}")
		sock.sendall(encoded_verification_msg)
		# asteptam confirmare
		print(f"* Asteptam ACK corespunzator")
		ack = sock.recv(1024)
		# am primit ACK
		ack_data = data_decode(ack)
		print(f">>> Am primit ack pentru mesajul trimis : {ack_data}")
		time.sleep(1)
	print("* Handshake realizat cu succes!")
	return True

# functia care trimite mesaje de verificare a conexiunii prin UART
def UARTConnectionCheck(port) -> bool:
	# vom trimite 3 mesaje pentru care asteptam confirmare imediata
	print("\n\n")
	# vom trimite 3 mesaje pentru care asteptam confirmare imediata
	for index in range(1,4):
		# compunem mesajul
		verification_msg = f"[HS] MSG{index}"
		# encodam mesajul
		encoded_verification_msg = data_encode(verification_msg)
		# trimitem mesajul
		print(f"* Am trimis MSG{index}")
		port.write(encoded_verification_msg)
		# asteptam confirmare
		print(f"* Asteptam ACK corespunzator")
		ack = port.read()
		remaining_bytes = port.inWaiting()
		ack += port.read(remaining_bytes)
		# am primit ACK
		ack_data = data_decode(ack)
		print(f">>> Am primit ack pentru mesajul trimis : {ack_data}")
		time.sleep(1)
	print("* Handshake realizat cu succes!")
	return True
