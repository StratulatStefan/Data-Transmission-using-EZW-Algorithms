import re
import time

# functie lambda care codifica un mesaj din format string in format binar
data_encode = lambda message : message.encode("utf-8")

# functie lambda care decodifica un mesaj din format binar in format string
data_decode = lambda message : message.decode("utf-8")

# functie lambda care identifica modalitatea de comunicare pe baza string-ului
communication_type = lambda message : 0 if "TCP" in message else 1 if "UART" in message else None

# functie lambda care returneaza continutul necesar din mesajul specific Handshake-ului
# se elimina componenta "[HS] "
relevant_data_handshake = lambda message : re.findall("\[HS\]\s(.+)", message)[0]

# functie lambda care extrage un numar dintr-un string
# folosita in cazul extragerii index-ului din ACK-ul specific Handshake-ului
extract_number = lambda message : re.findall("[0-9]+", message)[0]


# functie folosita pentru transmiterea octetilor prin socket-ul TCP
def socketWRITE(sock, message):
        # trimitem mesajul in format binar
	sock.sendall(message)

# functie folosita pentru transmiterea unui mesaj prin socket-ul TCP
def socketWRITEMessage(sock, message):
        # encodam messajul
	encoded_msg = data_encode(message)
	# trimitem mesajul
	socketWRITE(sock, encoded_msg)

# functie folosita pentru transmiterea octetilor prin UART
def uartWRITE(port, message):
        # trimitem mesajul encodat
	port.reset_output_buffer()
	port.write(message)

# functie folosita pentru transmiterea unui mesaj prin UART
def uartWRITEMessage(port, message):
        # encodam mesajul
	encoded_msg = data_encode(message)
        # trimitem mesajul encodat
	uartWRITE(port, encoded_msg)

# functie pentru citirea octetilor din socket-ul TCP
def socketREAD(sock):
        # citim si returnam 1024 de octeti din socket
		return sock.recv(1024)

# functie pentru citirea unui mesaj de pe socket-ul TCP
def socketREADMessage(sock):
        # citim octetii din socket
	message = socketREAD(sock)
        # decodam si returnam octetii
	return data_decode(message)

# functie pentru citirea octetilor din UART
def uartREAD(port):
	# citim 1 octet de pe portul serial
	data = port.read()
	time.sleep(0.075)
        # determinam numarul de octeti ramasi in bufferul de intrare
	remaining_bytes = port.inWaiting()
        # citim octetii ramasi
	data += port.read(remaining_bytes)
	port.reset_input_buffer()
	return data

# functie pentru citirea unui mesaj din UART
def uartREADMessage(port):
        # citim octetii din UART
	data = uartREAD(port)
        # decodam si returnam mesajul
	return data_decode(data)

# functie pentru transformarea unui string intr-un dictionar
def StringToDictionary(message : str) -> dict :
	result = {}
	# eliminam parantezele acolade delimitatoare care se afla pe prima si ultima pozitie
	message = message[1:-1]
	# - elementele sunt delimitate prin virgule, asa ca spargem string-ul in mai multe
	# substring-uri, avand virgula ca delimitator
	components = message.split(",")
	# in acest punct, avem componente de forma : "cheie" : "valoare"
	for component in components:
		# eliminam ghilimelele si spatiile libere
		component = component.replace("\"","")
		component = component.replace("\'","")
		component = component.replace(" ","")
		# spargem componenta dupa ":"
		key, value = component.split(":")
		result[f"{key}"] = value

	return result
