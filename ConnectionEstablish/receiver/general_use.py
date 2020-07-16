import re

# functie lambda care codifica un mesaj din format string in format binar
data_encode = lambda message : message.encode("utf-8")

# functie lambda care decodifica un mesaj din format binar in format string
data_decode = lambda message : message.decode("utf-8")

# functie lambda care identifica modalitatea de comunicare
communication_type = lambda message : 0 if "TCP" in message else 1 if "UART" in message else None

# functie lambda care returneaza continutul necesar din mesajul specific Handshake-ului
relevant_data_handshake = lambda message : re.findall("\[HS\]\s(.+)", message)[0]

# functie lambda care extrage un numar dintr-un string
# folosita in cazul extragerii index-ului din ACK
extract_number = lambda message : re.findall("[0-9]+", message)[0]


# functie folosita pentru transmiterea octetilor prin socket TCP
def socketWRITE(sock, message):
        # trimitem mesajul encodat
	sock.sendall(message)

# functie folosita pentru transmiterea unui mesaj prin socket TCP
def socketWRITEMessage(sock, message):
        # encodam messajul
	encoded_msg = data_encode(message)
	socketWRITE(sock, encoded_msg)

# functie folosita pentru transmiterea octetilor prin UART
def uartWRITE(port, message):
        # trimitem mesajul encodat
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
        # determinam numarul de octeti ramasi in bufferul de intrare
	remaining_bytes = port.inWaiting()
        # citim octetii ramasi
	data += port.read(remaining_bytes)
	return data

# functie pentru citirea unui mesaj din UART
def uartREADMessage(port):
        # citim octetii din UART
	data = uartREAD(port)
        # decodam si returnam mesajul
	return data_decode(data)

