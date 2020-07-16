from general_use import *
import time
import serial


# - functie care realizeaza handshake-ul cu clientul pentru a-l informa cu privire la modalitatea de comunicare
# aleasa si pentru a stabili conexiunea cu acesta
def CommunicationHandshake(TCPConnection, comselection) -> bool:
	print("**********************************")
	 # raspuns returnat in cazul in care handshake-ul a esuat
	ErrorResponse = None, None, False
	print("Handshake\n")
	# identificam modalitatea de comunicare
	communication = "UART" if comselection == 1 else "TCP" if comselection == 0 else None
	# formam mesajul de initializare a Handshake-ului
	initMessage = f"[HS] INIT {communication}"
	# trimitem mesajul catre client prin canalul de comunicare
	print("* Trimitem mesajul de initiere a handshake-ului catre client!")
	socketWRITEMessage(TCPConnection,initMessage)
	print(">>> Initializare trimisa cu succes!")
	print("* Asteptam ACK de la client!")
	# asteptam primirea ack-ului de la client, pentru a indica daca a salvat modalitatea de comunicare
	ackdata = socketREADMessage(TCPConnection)
	print(f">>> Am primit ACK de la client : {ackdata}!")
	if "STARTED" not in ackdata :
		# nu am primit mesajul de raspuns corect!
		pass
		# return ErrorResponse
	# incepem secventa de trimitere de mesaje de verificare pe canalul de comunicare stabilit
	print(f"* Incepem secventa de verificare specifica {communication}...")
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
		connection = serial.Serial("/dev/ttyS0", baudrate = 576000, timeout=None)

	# variabila booleana care retine daca tipul de comunicare specificat este invalid
	invalidcomselection = comselection < 0 or comselection > 1
	if invalidcomselection or not ConnectionCheck(connection, comselection):
		# - handshake esuat daca tipul de comunicare specificat este invalid sau
		# daca trimiterea de mesaje intre cele doua medii a esuat!
		return ErrorResponse

	# handshake efectuat cu succes!
	return comselection, connection, True
	print("**********************************\n\n")

# functia care trimite mesaje de verificare a conexiunii, corespunzator mediului de comunicare ales
def ConnectionCheck(connection, selection) -> bool:
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
		print(f"* Am trimis MSG{index}")
		writeFunction(connection, verification_msg)
		# asteptam confirmare
		print(f"* Asteptam ACK corespunzator")
		ack_data = readFunction(connection)
		# am primit ACK
		print(f">>> Am primit ack pentru mesajul trimis : {ack_data}")
		time.sleep(1)
	print("* Handshake realizat cu succes!")
	return True
