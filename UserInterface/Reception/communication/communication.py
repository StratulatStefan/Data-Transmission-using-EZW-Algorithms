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

# functia care realizeaza comunicarea cu celalalt nod
def Communication(gui_handler, printer, connection, type):
	global significance_map
	global reconstruction_values

	# determinam tipul comunicatiei si setam functiile coresp. pentru citire/scriere
	read_fun = socketREAD if type == 0 else uartREAD if type == 1 else None
	write_fun = socketWRITEMessage if type == 0 else uartWRITEMessage if type == 1 else None

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
	finish_found = False
	sig_map = ""
	rec_vals = ""

	# bucla infinita pentru receptia de pachete de octeti
	printer("Waiting for data...")
	while True:
		parameters_found = False
		# asteptam (blocant) receptionarea a 1024 de octeti
		data = read_fun(connection)

		# definim conditia de finalizare a trimiterii tuturor datelor
		if CheckForParameter(data, "finish") :
			finish_found = True
			printer("Am primit toate datele necesare!")
			write_fun(connection, "* Trimitem confirmare pentru primirea mesajului de incheiere a trimiterii tututor pachetelor!")

			gui_handler.current_iteration.setText(str(0))
			gui_handler.current_iteration.repaint()
			gui_handler.app.processEvents()

		# definim conditia de incepere a unei noi iteratii de primire a coeficientilor
		elif CheckForParameter(data, "start"):
			if finish_found == True:
				printer("Primim o noua imagine...")
				time.sleep(1)
				finish_found = False
			# curatam obiectele corespunzatoare
			significance_map = []
			reconstruction_values = []
			delimiter_found = False
			sig_map = ""
			rec_vals = ""
			printer("Incepem primirea coeficientilor!")
			write_fun(connection, "* Trimitem confirmare pentru primirea mesajului de receptionare a pachetelor la o noua iteratie!")

			current_iteration = int(gui_handler.current_iteration.toPlainText()) + 1
			gui_handler.current_iteration.setText(str(current_iteration))
			gui_handler.current_iteration.repaint()
			gui_handler.app.processEvents()
			continue
		# definim conditia de finalizare a unei iteratii
		elif CheckForParameter(data, "stop"):
			# in acest moment am primit toate datele necesare recompunerii imaginii la iteratia curenta
			# apelam functia de decodificare si reconstructie
			# recompunem listele corespunzatoare
			significance_map = list(filter(lambda value : value != "", sig_map.split(",")))
			significance_map = list(map(lambda value: int(value), significance_map))

			print(len(significance_map))
			reconstruction_values = list(filter(lambda value : value != "", rec_vals.split(",")))
			reconstruction_values = list(map(lambda value: int(value), reconstruction_values))

			# realizam recompunerea coeficientilor pe baza significance map si reconstruction values
			# totodata, se recompune imaginea finala si se afiseaza pe interfata
			printer("Am primit significance map si reconstruction values!")
			gui_handler.DWTRecomposer(significance_map, reconstruction_values)
			write_fun(connection, "* Trimitem confirmare pentru mesajul de finalizare a unei iteratii!")
		# definim conditia de mijloc a trimiterii celor doua liste de coeficienti
		elif CheckForParameter(data, "delimitator"):
			# am primit delimitatorul, deci s-au trimis toate valorile din significance map
			# urmeaza sa se trimita valorile din reconstruction values
			delimiter_found = True
			write_fun(connection, "* Trimitem confirmare pentru primirea delimitatorului!")
			gui_handler.app.processEvents()
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
				parameters_found = True
				break
		if parameters_found == True:
			write_fun(connection, "* Trimitem confirmare pentru primirea unui parametru!")
			gui_handler.app.processEvents()
			continue
		else:
			# nu am primit un parametru sau vreo conditie de pornire/oprire,
			# primim significance map sau valorile de reconstructie
			data_recv = data.decode("utf-8")
			if delimiter_found == True:
				rec_vals += data_recv + ","
				#write_fun(connection, "* Trimitem confirmare pentru primirea reconstruction values!")
			else:
				sig_map += data_recv + ","
				#write_fun(connection, "* Trimitem confirmare pentru primirea significance map!")
