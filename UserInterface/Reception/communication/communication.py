from communication.general_use import *
import re
import os
import time


# obiecte globale ce vor contine datele specifice significance_map si reconstruction_values, primite de la celalalt nod
significance_map = []
reconstruction_values = []

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

# functie care extrage continutul mesajul ce contine parametru [<parametru>] <continut_mesaj>
def ExtractParameter(content):
	content = data_decode(content)
	pattern = "\s.+"
	matches = re.findall(pattern, content)
	return matches[0][1:]

# functia care realizeaza transmiterea fisierelor prin TCP
def TCPCommunication(gui_handler, printer, connection):
	global significance_map
	global reconstruction_values

	# tipurile de parametrii ce pot fi receptionati, mesajul specific fiecaruia si obiectul de pe interfata ce va fi modificat
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

	delimiter_found = False
	sig_map = ""
	rec_vals = ""

	# bucla infinita pentru receptia de pachete de octeti
	printer("Waiting for data...")
	while True:
		parameters_found = False
		# asteptam (blocant) receptionarea a 1024 de octeti
		data = socketREAD(connection)

		# definim conditia de finalizare a trimiterii tuturor datelor
		if CheckForParameter(data, "finish") : break
		# definim conditia de incepere a unei noi iteratii de primire a coeficientilor
		elif CheckForParameter(data, "start"):
			# curatam obiectele corespunzatoare
			significance_map = []
			reconstruction_values = []
			delimiter_found = False
			sig_map = ""
			rec_vals = ""
			continue
		# definim conditia de finalizare a unei iteratii
		elif CheckForParameter(data, "stop"):
			# in acest moment am primit toate datele necesare recompunerii imaginii la iteratia curenta
			# apelam functia de decodificare si reconstructie
			if sig_map[0] == ",":
				sig_map = sig_map[1:]
			if sig_map[-1] == ",":
				sig_map = sig_map[:-1]
			if rec_vals[0] == ",":
				rec_vals = rec_vals[1:]
			if rec_vals[-1] == ",":
				rec_vals = rec_vals[:-1]

			# recompunem listele corespunzatoare
			significance_map = list(map(lambda value: int(value), sig_map.split(",")))
			reconstruction_values = list(map(lambda value: int(value), rec_vals.split(",")))

			# realizam recompunerea coeficientilor pe baza significance map si reconstruction values
			# totodata, se recompune imaginea finala si se afiseaza pe interfata
			gui_handler.DWTRecomposer(significance_map, reconstruction_values)
		# definim conditia de mijloc a trimiterii celor doua liste de coeficienti
		elif CheckForParameter(data, "delimitator"):
			# am primit delimitatorul, deci s-au trimis toate valorile din significance map
			# urmeaza sa se trimita valorile din reconstruction values
			delimiter_found = True
			continue
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
				time.sleep(0.01)
				parameters_found = True
				break
		if parameters_found == True:
			continue
		else:
			# nu am primit un parametru sau vreo conditie de pornire/oprire,
			# primim significance map sau valorile de reconstructie
			data_recv = data.decode("utf-8")
			if delimiter_found == True:
				rec_vals += data_recv
			else:
				sig_map += data_recv

# functia care realizeaza transmiterea fisierelor prin UART
def UARTCommunication(gui_handler, printer, connection):
	global significance_map
	global reconstruction_values

	# tipurile de parametrii ce pot fi receptionati, mesajul specific fiecaruia si obiectul de pe interfata ce va fi modificat
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

	delimiter_found = False
	sig_map = ""
	rec_vals = ""

	# bucla infinita pentru receptia de pachete de octeti
	printer("Waiting for data...")
	while True:
		parameters_found = False
		# asteptam (blocant) receptionarea a 1024 de octeti
		data = uartREAD(connection)

		# definim conditia de finalizare a trimiterii tuturor datelor
		if CheckForParameter(data, "finish"):
			break
		# definim conditia de incepere a unei noi iteratii de primire a coeficientilor
		elif CheckForParameter(data, "start"):
			# curatam obiectele corespunzatoare
			significance_map = []
			reconstruction_values = []
			delimiter_found = False
			sig_map = ""
			rec_vals = ""
			continue
		# definim conditia de finalizare a unei iteratii
		elif CheckForParameter(data, "stop"):
			# in acest moment am primit toate datele necesare recompunerii imaginii la iteratia curenta
			# apelam functia de decodificare si reconstructie
			if sig_map[0] == ",":
				sig_map = sig_map[1:]
			if sig_map[-1] == ",":
				sig_map = sig_map[:-1]
			if rec_vals[0] == ",":
				rec_vals = rec_vals[1:]
			if rec_vals[-1] == ",":
				rec_vals = rec_vals[:-1]

			# recompunem listele corespunzatoare
			significance_map = list(map(lambda value: int(value), sig_map.split(",")))
			reconstruction_values = list(map(lambda value: int(value), rec_vals.split(",")))

			# realizam recompunerea coeficientilor pe baza significance map si reconstruction values
			# totodata, se recompune imaginea finala si se afiseaza pe interfata
			gui_handler.DWTRecomposer(significance_map, reconstruction_values)
		# definim conditia de mijloc a trimiterii celor doua liste de coeficienti
		elif CheckForParameter(data, "delimitator"):
			# am primit delimitatorul, deci s-au trimis toate valorile din significance map
			# urmeaza sa se trimita valorile din reconstruction values
			delimiter_found = True
			continue
		# verificam daca am primit un parametru : mesaj de tipul "[type] content"
		for parameter in parameters:
			if CheckForParameter(data, parameter["type"]):
				# am primit un parametru
				# facem conversia la string si il salvam
				parameter_data = ExtractParameter(data)
				printer(f'* Am primit {parameter["text_label"]} : {parameter_data}!')
				# setam numele pe labelul de pe interfata
				parameter["ui_object"].setText(parameter_data)
				parameter["ui_object"].repaint()
				time.sleep(0.01)
				parameters_found = True
				break
		if parameters_found == True:
			continue
		else:
			# nu am primit un parametru sau vreo conditie de pornire/oprire,
			# primim significance map sau valorile de reconstructie
			data_recv = data.decode("utf-8")
			if delimiter_found == True:
				rec_vals += data_recv
			else:
				sig_map += data_recv
