# functie lambda care codifica un mesaj din format string in format binar
data_encode = lambda message : message.encode("utf-8")

# functie lambda care decodifica un mesaj din format binar in format string
data_decode = lambda message : message.decode("utf-8")