from communication.general_use import * 
import time 
import serial


# - functie care realizeaza handshake-ul cu clientul pentru a-l informa cu privire la modalitatea de comunicare
# aleasa si pentru a stabili conexiunea cu acesta
def CommunicationHandshake(printer, TCPConnection, comselection) -> bool:
	# raspuns returnat in cazul in care handshake-ul a esuat
	ErrorResponse = None, None, False
	printer("Handshake\n")
	# identificam modalitatea de comunicare
	communication = "UART" if comselection == 1 else "TCP" if comselection == 0 else None
	# formam mesajul de initializare a Handshake-ului
	reloads = 1
	while True:
		initMessage = f"[HS] INIT {communication}"
		#initMessage = f"INIT {communication}"
		# trimitem mesajul catre client prin canalul de comunicare
		printer("\n* Trimitem mesajul de initiere a handshake-ului catre client!")
		socketWRITEMessage(TCPConnection,initMessage)
		printer(">>> Initializare trimisa cu succes!")
		printer("* Asteptam ACK de la client!")
		# asteptam primirea ack-ului de la client, pentru a indica daca a salvat modalitatea de comunicare
		ackdata = socketREADMessage(TCPConnection)
		printer(f">>> Am primit ACK de la client : {ackdata}!")
		if "Waiting" in ackdata:
			# am primit un ack gresit..
			if reloads == 3:
				# se permit doar 3 erori! Returnam eroare!
				printer("* Am primit un ack eronat de prea multe ori! Intrerupem!")
				return ErrorResponse
			# incercam retransmisia
			printer("* Am primit un ack eronat! Reluam handshake-ul!")
			reloads += 1
			time.sleep(1)
			continue
		else:
			reloads = 1

		if "STARTED" not in ackdata :
			# nu am primit mesajul de raspuns corect!
			if reloads == 3:
				# se permit doar 3 erori! Returnam eroare!
				printer("* Am primit ack eronat de prea multe ori! Intrerupem!")
				return ErrorResponse
			# incercam retransmisia
			printer("* Am primit un ack eronat! Relaum handshake-ul!")
			reloads += 1
			time.sleep(1)
			continue
		else:
			reloads = 1
			break

	# incepem secventa de trimitere de mesaje de verificare pe canalul de comunicare stabilit
	printer(f"* Incepem secventa de verificare specifica {communication}...")
	# identificam tipul de comunicare necesar pe baza tipului specificat
	connection = None
	if comselection == 0:
		# pastram instanta la socket-ul initiat in main
		connection = TCPConnection
	elif comselection == 1:
		# definim un port pentru comunicarea seriala
		# portul pe care se va mapa UART : /dev/ttyS0
		# viteza de transfer : 576000 biti pe secunda
		# astepta a primirii raspunsului la infinit : timeout = None
		connection = serial.Serial("/dev/ttyS0", baudrate = 921600, timeout=None, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, rtscts=False)

	# variabila booleana care retine daca tipul de comunicare specificat este invalid
	invalidcomselection = comselection < 0 or comselection > 1
	if invalidcomselection or not ConnectionCheck(printer,connection, comselection):
		# - handshake esuat daca tipul de comunicare specificat este invalid sau
		# daca trimiterea de mesaje intre cele doua medii a esuat!
		return ErrorResponse

	# handshake efectuat cu succes!
	print(connection)
	return comselection, connection, True

# functia care trimite mesaje de verificare a conexiunii, corespunzator mediului de comunicare ales
def ConnectionCheck(printer,connection, selection) -> bool:
	# determinam functiile necesare pentru citire si scriere, pe baza tipul de comunicare ales
	# folosim referinte la acele functii
	readFunction = uartREADMessage if selection == 1 else socketREADMessage if selection == 0 else None
	writeFunction = uartWRITEMessage if selection == 1 else socketWRITEMessage if selection == 0 else None

	print("\n\n")
	# vom trimite 3 mesaje pentru care asteptam confirmare imediata
	for index in range(1,4):
		# compunem mesajul
		verification_msg = f"[HS] MSG{index}"
		# trimitem mesajul
		printer(f"* Am trimis MSG{index}")
		time.sleep(0.05)
		writeFunction(connection, verification_msg)
		# asteptam confirmare
		printer(f"* Asteptam ACK corespunzator")
		time.sleep(0.05)
		ack_data = readFunction(connection)
		# am primit ACK
		printer(f">>> Am primit ack pentru mesajul trimis : {ack_data}")
		time.sleep(0.5)
	printer("* Handshake realizat cu succes!")
	return True
