'''
*   Mediul de dezvoltare QT genereaza interfata grafica sub forma unui fisier cu extensia ".ui" .
*   Asadar, pentru a obtine fisierul sursa python ce va contine codul interfetei grafice, vom folosi utilitarul
"pyside2-uic", care va primi ca input fisierul cu interfata de tip ".uic" si va avea ca output codul sursa de tip ".py"
*   Aceasta trebuie realizata inainte de a incarca codul sursa al interfetei in program si a-l utiliza.
'''

# inainte de a incarca codul sursa generat de QT, vom face conversia de la .ui la .py folosind pyside2-uic
import os
import multiprocessing

from PySide2.QtCore import QTimer, QThread


from api.wavelets import *
import time
#os.system("pyside2-uic receiver.ui > receiver_gui.py")

# - am facut conversia interfetei la cod sursa; urmeaza, asadar, sa incarcam acest cod in programul principal si sa il
# utilizam
from worker import *
from communication.handshake import *
from communication.communication import *
from api.decoder import *
import socket
import serial
import threading

# definim un obiect global care va contine imaginea ce va fi incarcata din GUI
# acest obiect va fi folosit in prelucrarile ulterioare din algoritm
global_image = []

# definim obiectul global ce va contine descompunerea imaginii in coeficienti Wavelet
wavelet_decomposition = []

# definim un obiect care va contine o instanta a conexiunii dintre cele doua noduri
connection = None

# definim un obiect care va contine o instanta a socket-ului prin care se va realiza conexiunea
sock = None

# definim un obiect de tip Boolean folosit pentru validarea stabilirii conexiunii
connection_established = False

# definim credentialele de realizare a conexiunii
config = {
	#"host" : "192.168.43.43", # HOST-ul serverului
    "host" : "192.168.43.226", # HOST-ul serverului
    "port" : 7000		  # PORT-ul pe care este mapat serverul
}

# functie apelata la inchiderea ferestrei, pentru inchiderea sigura a conexiunii cu celalalt nod
def SafeClose():
    if connection_established == True:
        print("Safe Close! Good Bye!")
        connection.close() if connection != None else None
        sock.close() if sock != None else None

class GraphicalUserInterface(Ui_MainWindow):
    def __init__(self, window, app):
        self.setupUi(window)
        self.app = app
        self.consoleLock = threading.RLock()

    # setam interactiunile posibile ale interfetei grafice
    def SetActions(self):
        self.current_iteration.setText(str(0))
        self.current_iteration.repaint()
        self.current_iteration.toPlainText()
        # atasam functia de callback pentru cautarea si stabilirea de conexiuni
        self.check_connections.clicked.connect(self.CheckForConnections)

    # functie pentru tratarea unei exceptii prin afisarea un messagebox cu textul exceptiei
    def HandleBasicException(self, exc):
        # definim un messageBox si setam textul exceptiei
        messageBox = QMessageBox()
        messageBox.setText(str(exc))

        # setam icon-ul si titlul
        messageBox.setIcon(QMessageBox.Warning)
        messageBox.setWindowTitle("Exception")

        # setam butoanele standard
        messageBox.setStandardButtons(QMessageBox.Ok)

        # afisam messageBox-ul
        messageBox.exec_()

    # functie pentru setarea label-ului ce descrie statusul conexiunii
    def SetConnectionStatus(self, text):
        #self.consoleLock.acquire()
        self.connection_status.setText(text)
        self.connection_status.repaint()
        #self.consoleLock.release()
        time.sleep(0.05)

        self.app.processEvents()

    # functie care incearca conectarea cu celalalt nod
    # functia salveaza instanta conexiunii intr-un obiect global
    def CheckForConnections(self):
        global connection_established
        global sock
        global connection

        # verificare coresp celei de-a doua stari a butonului, cea de oprire a conexiunii
        if connection_established == True:
            sock.close()
            self.SetConnectionStatus("Conexiunea a fost inchisa cu succes...")
            return

        self.SetConnectionStatus("Se deschide socket-ul...")
        time.sleep(0.5)
        # AF-INET pentru familia de adrese IPv4
        # SOCK_STREAM pentru comunicare prin TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SetConnectionStatus("Socket-ul a fost deschis cu succes...")
        time.sleep(0.5)
        self.SetConnectionStatus("Se realizeaza conectarea la server...")
        time.sleep(0.5)
        # se realizeaza conectarea la server
        sock.connect((config["host"], config["port"]))
        self.SetConnectionStatus("Conectare realizata cu succes...")

        # modificam butonul de realizare a conexiunii si setam flagul coresp.
        self.check_connections.setText("Stop connection")
        connection_established = True
        time.sleep(1)

        self.SetConnectionStatus("Se asteapta date...")
        communication_type = None

        # bucla infinita de comunicare dintre server si client
        while True:
			# asteptam primirea unui mesaj pe socket
            self.SetConnectionStatus("I'm fucking waiting for data...[Infinite Loop]\n")
            decoded_data = socketREADMessage(sock)
            self.SetConnectionStatus(f"* Am primit mesajul : {decoded_data}!")

            if "[HS]" not in decoded_data:
				# aceasta secventa se ocupa doar de realizeaza handshake-ului
				# un mesaj care cu contine identificatorul de handshake este un mesaj eronat
				# transmitem un mesaj de eroare!
                errorMessage = "Waiting for handshake!"
                socketWRITEMessage(sock, errorMessage)
            else:
				# se realizeaza Handshake-ul
                type, connection, handshake_state = CommunicationHandshake(self.SetConnectionStatus, sock, decoded_data)
                if not handshake_state :
					# handshake esuat
                    self.check_connections.setText("* Handshake-ul a esuat!")
                    # informam serverul ca handshake-ul a esuat!
                    errorMessage = "Handshake error!"
                    socketWRITEMessage(sock, errorMessage)
                    # - astfel, asteptam reincercarea executiei handshake-ului la urmatoarea parcurgere a buclei
                else:
                    # handshake efectuat cu succes
                    if type == 0:
                        # initiem comunicarea prin TCP
                        self.SetConnectionStatus("Handshake realizat cu succes!\nComunicare : TCP Sockets")
                        communication_type = 0
                    elif type == 1:
						# initiem comunicarea prin UART
                        self.SetConnectionStatus("Handshake realizat cu succes!\nComunicare : UART")
                        communication_type = 1
                    else:
						# am primit un tip eronat de comunicare
                        print("* Canal de comunicare ales eronat!")
						# asteptam reluarea handshake-ului si primirea unui tip valid
                    break

        # curatam consola de afisare a statusului!
        self.connection_status.clear()
        if communication_type in [0, 1]:
            # daca am ajuns aici, inseamna ca handshake-ul a fost efectua cu succes si putem incepe transmiterea
            Communication(self, self.SetConnectionStatus, connection, type)

    # functie care va prelua datele receptionate si va recompune imaginea
    def DWTRecomposer(self, significance_map, reconstruction_values):
        # extragem nr. nivelelor de descompunere
        decomposition_levels = int(self.image_decomposition_levels.toPlainText())

        # exragem coordonatele dimensionale are transformatei
        coordinates = self.image_dimensions.toPlainText().lower().replace(" ","")
        rows, cols = list(map(lambda value : int(int(value) / 1), coordinates.split("x")))

        # extragem conventiile de codificare a significance map
        significance_map_conventions = StringToDictionary(self.significance_map_conventions.toPlainText())

        DWT = SendEncodings(decomposition_levels, (rows, cols), significance_map_conventions,
                            significance_map, reconstruction_values)

        pixmapDWT = UI_Worker.ConvertNumpyImagetoPixmap(DWT)

        width = self.wavelet_label.width()
        height = self.wavelet_label.height()
        self.wavelet_label.setPixmap(pixmapDWT.scaled(width,height, Qt.KeepAspectRatio))
        self.wavelet_label.repaint()

        # avand vectorul cu coeficientii DWT, putem recompune imaginea originala
        self.ImageReconstruction(DWT, decomposition_levels)

    # functie care reconstruieste imaginea originala pe baza coeficientilor receptionati
    def ImageReconstruction(self, DWT, decomposition_levels):
        # determinam tipul de algoritm folosit
        decomposition_algorithm = self.wavelet_algorithm.toPlainText().lower()

        # determinam tipul de wavelet folosit
        wavelet_type = self.wavelet_type.toPlainText().lower()

        image = None
      
        rows, cols = DWT.shape
        levels = int(np.power(2, decomposition_levels))
        wavelet_type = defined_filters[wavelet_type]
        while levels != 1:
            rows, cols = list(map(lambda value : int(value / levels), DWT.shape))
            coeffs = (DWT[:rows, :cols],
                    (DWT[:rows, cols : int(cols * 2)],
                    DWT[rows: int(rows * 2), :cols],
                    DWT[rows: int(rows * 2), cols:int(cols * 2)]))
            image = pywt.idwt2(coeffs, "haar")
            DWT[:int(rows * 2), : int(cols * 2)] = image
            levels = int(levels / 2)

        image = UI_Worker.ConvertNumpyImagetoPixmap(image)
        width, height = self.image_label.width(), self.image_label.height()
        self.image_label.setPixmap(image.scaled(width, height, Qt.KeepAspectRatio))
        self.image_label.repaint()




