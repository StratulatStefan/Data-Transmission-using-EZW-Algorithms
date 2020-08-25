from communication.general_use import *
import re
import os
import time
from api.decoder import *
import sys

# numele fisierului se identifica astfel : [nume] <nume_fisier>.<extensie>
def CheckForFileName(content):
	return CheckForParameter(content, "filename")

# functie care verifica daca mesajul primit reprezinta un parametru
# parametrul nu poate fi identificat daca:
# 1). nu contine [tip_parametru]
# 2). primim exceptie din cauza imposibilitatii de a decoda octetii la codec-ul utf-8
def CheckForParameter(content, type):
	try:
		data = data_decode(content)
		if f"[{type}]" in data:
			return True
	except UnicodeDecodeError:
		pass
	return False

# functie care extrage numele fisierului din mesajul primit
def ExtractParameter(content):
	content = data_decode(content)
	pattern = "\s.+"
	matches = re.findall(pattern, content)
	return matches[0][1:]

# functie care verifica daca fisierul pe care dorim sa il scriem exista
def CheckForExistanceAndDelete(filename):
	if os.path.exists(filename):
		# -fisierul exista pe disc, deci trebuie sters, deoarece 
		# scrierea in fisier se face secvential, folosind "ab" (append binary)
		os.remove(filename)

# functia care realizeaza transmiterea fisierelor prin TCP
def TCPCommunication(gui_handler, printer, connection):
	global significance_map
	printer("-------------------------------")
	# bucla infinita pentru receptia de pachete de octeti
	parameters_found = False



	parameters = [{"type": "filename",
				   "text_label": "numele imaginii",
				   "ui_object": gui_handler.image_name},
				  {"type": "dimensions",
				   "text_label": "dimensiunile imaginii",
				   "ui_object": gui_handler.image_dimensions},
				  {"type": "size",
				   "text_label": "dimensiunea imaginii",
				   "ui_object": gui_handler.image_size},
				  {"type": "decomposition_levels",
				   "text_label": "nr. nivelelor de descompunere",
				   "ui_object": gui_handler.image_decomposition_levels},
				  {"type": "decomposition_type",
				   "text_label": "algoritmul de descompunere",
				   "ui_object": gui_handler.wavelet_algorithm},
				  {"type": "wavelet_type",
				   "text_label": "tipul de wavelet folosit",
				   "ui_object": gui_handler.wavelet_type},
				  {"type": "iteration_loops",
				   "text_label": "nr. de iteratii de codificare",
				   "ui_object": gui_handler.image_expected_iterations},
				  {"type": "conventions",
				   "text_label": "conventiile significance map",
				   "ui_object": gui_handler.significance_map_conventions},
				  ]
	while True:
		printer("Waiting for data...")
		# asteptam (blocant) receptionarea a 1024 de octeti
		data = socketREAD(connection)

		# verificam daca am primit un parametru : mesaj de tipul "[type] content"
		for parameter in parameters:
			if CheckForParameter(data, parameter["type"]):
				# am primit un parametru
				# facem conversia la string si il salvam
				parameter_data = ExtractParameter(data)
				printer(f'* Am primit {parameter["text_label"]} : {parameter_data}!')
				#setam numele pe labelul de pe interfata
				parameter["ui_object"].setText(parameter_data)
				parameter["ui_object"].repaint()
				time.sleep(0.25)
				parameters_found = True
				break
		if parameters_found == True:
			continue
		else:
			# nu am primit un parametru, deci primim significance map sau valorile de reconstructie
			printer("* Am primit un pachet de date!")
			significance_map.append(data)
	print(significance_map)
	x = 0



# functia care realizeaza transmiterea fisierelor prin UART
def UARTCommunication(gui_handler, printer, connection):
	# bucla infinita pentru asteptarea de pachete de octeti
	while True:
		print("----------------------------------------")
		print("[Waiting for data]")

		# citim un octet de pe portul serial
		data_chunk = connection.read()
		time.sleep(0.01)

		# identificam si citim restul octetilor de pe portul serial
		remaining_bytes = connection.inWaiting()
		data_chunk += connection.read(remaining_bytes)

		# - verificam daca mesajul primit reprezinta numele fisierului
		# sau un pachet de octeti ce compun fisierului
		if CheckForFilename(data_chunk):
			data_chunk = data_decode(data_chunk)
			filename = ExtractFileName(data_chunk)
			print(f"[Am primit numele fisierului : \"{filename}\"]")
			CheckForExistanceAndDelete(filename)
			time.sleep(0.1)
		else:
			# primim pachete de octeti care compun fisierul
			print(f"[Am primit {remaining_bytes + 1} octeti pe portul serial.]")
			# folosim with pentru inchiderea automata a fisierului
			# - folosim "ab" (append binary), deoarece scrierea fisierului
			# se face secvential, la fiecare iteratie a buclei while
			# -nu dorim sa pastram fisierul in memorie si sa il scriem la final
			# dorim sa scriem fisierul pe masura ce primim octetii
			with open(filename, "ab") as file:
				file.write(data_chunk)
		#	pass
