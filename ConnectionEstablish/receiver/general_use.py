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