'''
*   Mediul de dezvoltare QT genereaza interfata grafica sub forma unui fisier cu extensia ".ui" .
*   Asadar, pentru a obtine fisierul sursa python ce va contine codul interfetei grafice, vom folosi utilitarul
"pyside2-uic", care va primi ca input fisierul cu interfata de tip ".uic" si va avea ca output codul sursa de tip ".py"
*   Aceasta trebuie realizata inainte de a incarca codul sursa al interfetei in program si a-l utiliza.
'''
import pickle
import os

# inainte de a incarca codul sursa al interfetei, vom face conversia de la .ui la .py folosind pyside2-uic
#os.system("pyside2-uic transmission.ui > transmission_gui.py")

# - am facut conversia interfetei la cod sursa; urmeaza, asadar, sa incarcam acest cod in programul principal si il utilizam
import socket
import sys
import serial
import time

from PySide2.QtCore import QUrl
from transmission_gui import *
from worker import *
from api.zerotree import *
from api.encoder import *
from communication.handshake import *
from api.wavelets import *
from threading import RLock

# definim un obiect global care va contine imaginea ce va fi incarcata din GUI
# acest obiect va fi folosit in prelucrarile ulterioare din algoritm
global_image = []

# definim obiectul global ce va contine descompunerea imaginii in coeficienti Wavelet
wavelet_decomposition = []

# definim un obiect care va contine o instanta a socket-ului prin care se va realiza conexiunea
sock = None

# definim un obiect care va contine o instanta a conexiunii dintre cele doua noduri
connection = None

# definim un obiect de tip Boolean folosit pentru validarea stabilirii conexiunii
connection_established = False

# definim un dictionar care va contine credentialele de comunicare
config = {
	"host" : "192.168.100.170",
	"port" : 7000 		  # PORT-ul pe care serverul asculta
}

# aceasta functie va fi apelata la inchiderea ferestrei si se va ocupa de inchiderea conexiunii cu celalalt nod
def SafeClose():
    if connection_established == True:
        print("Safe Close! Good Bye!")
        connection.close() if connection != None else None
        sock.close() if sock != None else None


class GraphicalUserInterface(Ui_MainWindow):
    def __init__(self, window):
        self.setupUi(window)
        window.setFixedSize(window.size())
        self.ExtraObjectAttributes()
        self.consoleLock = RLock()

    # - functie care adauga anumite atribute elementelor interfetei
    # - adaugarea acestor atribute se efectueaza aici intrucat, la fiecare modificare a interfetei grafice, codul sursa al
    # acesteia se modifica, urmand ca toate modificarile facute de dezvoltator sa fie eliminate din codul sursa
    # - asadar, le adaugam in clasa care mosteneste clasa generata de convertor si care nu va fi afectata de conversie
    def ExtraObjectAttributes(self):
        # elementul (box) care contine toti parametrii imaginii va fi invizibil pana la afisare imaginii
        self.image_parameters.setVisible(False)

        # la fel si pentru box-ul ce va contine reprezentarea descompunerii DWT
        self.wavelet_parameters.setVisible(False)

        # eliminam marginile acestui box de elemente (pt imagine si pt. DWT)
        # vom folosi o abordare de tip CSS
        # setam un nume (id, in contextul css) pentru acest element box
        self.image_parameters.setObjectName("image_parameters")
        self.wavelet_parameters.setObjectName("wavelet_parameters")

        # eliminam marginile
        self.image_parameters.setStyleSheet("QGroupBox#image_parameters {border : none}")
        self.wavelet_parameters.setStyleSheet("QGroupBox#wavelet_parameters {border : none}")

    # functie care trateaza apasarea butonului de cautare a unui fisier
    def HandleSearchImageButton(self):
        # adresa imaginii se va afla in elementul "image_source"
        # vom deschide un File Dialog de unde utilizatorul va selecta un fisier

        # definim un obiect de tip FileDialog
        fileDialog = QFileDialog()

        # setam tipurile de fisiere admise (imagini)
        fileDialog.setFileMode(QFileDialog.AnyFile)
        fileDialog.setNameFilter("Images (*.png *.jpg)")

        # deschidem File Dialog-ul si preluam url-ul
        if fileDialog.exec_():
            url = QUrl.toString(fileDialog.selectedUrls()[0])

        # prelucram url-ul astfel incat sa pastram doar sursa, eliminand protocolul (file:///)
        try:
            url = url.replace("file:///", "")
        except Exception:
            return

        # odata ce am extras url-ul, il setam in elementul image_source
        self.image_source.setText(url)

        # incarcam imaginea si o afisam in elementul corespunzator
        self.ImageLoadAndDisplay(url, self.image_label)

        # incarcam imaginea in obiectul ce va fi folosit de algoritm (un obiect de tip np.array)
        self.LoadNumpyImage(url)

        # elementul (box) care contine toti parametrii imaginii va fi vizibil
        self.image_parameters.setVisible(True)

    # setam interactiunile posibile ale interfetei grafice
    def SetActions(self):
        # atasam functia de callback pentru apasarea butonului de cautare a fisierului
        self.search_image.clicked.connect(self.HandleSearchImageButton)

        # atasam functia de callback pentru DWT
        self.wavelet_dec.clicked.connect(self.Wavelet_Decomposition)

        # atasam functia de callback pentru modificarea tipului de operatie DWT efectuata
        self.DWT_type.currentTextChanged.connect(self.SetWaveletTypes)

        # atasam functia de callback pentru codificarea cu ZeroTree si trimiterea catre celalalt nod
        self.encode_and_send.clicked.connect(self.ZeroTreeEncodingAndSend)

        # atasam functia de callback pentru cautarea si stabilirea de conexiuni
        self.check_connections.clicked.connect(self.CheckForConnections)

    # functie pentru incarcarea si afisarea imaginii
    def ImageLoadAndDisplay(self, path, image_label):
        # incarcam imaginea pentru afisare
        # vom folosi un obiect al librariei PySide2
        # (pentru prelucrarea imaginii, se va incarca folosind libraria OpenCV)
        qt_image = QPixmap(path)

        # convertim imaginea la grayscale
        qt_image = UI_Worker.GrayScalePixMap(qt_image)

        # extragem o serie din parametrii imaginii
        qt_image_parameters = self.ExtractImageParameters(qt_image)

        # obtinem dimensiunile label-ului
        width, height = self.image_label.width(), self.image_label.height()

        # afisam imaginea in elementul image_box si redimensionam label-ul astfel incat imaginea sa poata fi afisata complet
        image_label.setPixmap(qt_image.scaled(width, height, Qt.KeepAspectRatio))

        # setam parametrii imaginii in box-ul coresp.
        self.SetImageParameters([self.image_width, self.image_height, self.image_size, self.image_bpp], qt_image_parameters)

    # functie pentru incarcarea imaginii intr-un obiect de tip numpy.array, pentru folosirea ulterioara in cadrul algoritmului
    def LoadNumpyImage(self, url):
        global global_image
        try:
            global_image = ImageRead(url, cv.IMREAD_GRAYSCALE)
        except Exception as exc:
            self.HandleBasicException(exc)

    # functie pentru tratarea unei exceptii, prin afisarea un messagebox cu textul exceptiei
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

    # functie care extrage o serie de parametri ai unei imagini
    def ExtractImageParameters(self, image_map):
        # cream un dictionar care va contine parametrii extrasi
        parameters = {"width" : 0, "height" : 0, "size" : 0}
        parameters["width"] = image_map.width()
        parameters["height"] = image_map.height()

        # determinam nr. de biti necesari stocarii imaginii
        # imaginea este in grayscale, deci pentru fiecare pixel avem nevoie de 8 biti
        # reprezentarea se face in KBytes, deci impartim la 8 pentru a obtine Bytes si la 1024 pentru a obtine KBytes
        parameters["size"] = int(image_map.width() * image_map.height() * 8 / 8 / 1024)
        return parameters

    # functie care seteaza parametrii imaginii in elementul box corespunzator
    # vectorul elements va contine referinte la elementele grafice coresp.
    def SetImageParameters(self, elements, parameters):
        elements[0].setText(str(parameters["width"]))
        elements[1].setText(str(parameters["height"]))
        elements[2].setText(str(f'{parameters["size"]} KB'))
        if "time" in parameters.keys():
            elements[3].setText(f'{(round(parameters["time"], 4))} s')
        else:
            elements[3].setText(str(8))

    # functie care seteaza tipurile de Wavelet disponibile in functie de tipul de operatie efectuata
    def SetWaveletTypes(self):
        currentOperation = self.DWT_type.currentText().lower()
        wavelet_types = None
        if "pywavelets" in currentOperation:
            wavelet_types = ["Haar", "Biorthogonal", "Daubechies-1"]
        elif "convolution" in currentOperation or "linear-based" in currentOperation:
            wavelet_types = ["Daubechies",
                             "9-tap QMF pyramid",
                             "5-tap QMF pyramid"]

        # eliminam elementele din combobox
        self.wavelet_type.clear()

        # adaugam noile tipuri de wavelets in combobox
        for w_type in wavelet_types:
            self.wavelet_type.addItem(w_type)

    # - functie care se executa atunci cand o resursa nu este pregatita si nu vrem ca interfata sa se blocheze
    # - folosita in cazul descompunerii
    def VirtualProxy(self):
        # incarcam o imagina de asteptare si o afisam in fereastra wavelet_label
        qt_image = QPixmap("D:/Confidential/EZW Algorithm/loading.jpg")
        self.wavelet_label.setPixmap(qt_image.scaled(self.wavelet_label.width(),
                                                     self.wavelet_label.height(),
                                                     Qt.KeepAspectRatio))
        self.wavelet_label.repaint()

        # de asemenea, facem box-ul cu parametri invizibil
        self.wavelet_parameters.setVisible(False)
        self.wavelet_parameters.repaint()

        # - dupa ce descompunerea se va realiza cu succes, se vor apela functii in firul principal care vor
        # inlocui aceasta imagine si vor face campul de parametri vizibil

    # functie pentru tratarea DWT
    def Wavelet_Decomposition(self):
        global global_image
        global wavelet_decomposition
        # descompunerea se poate face doar daca imaginea este incarcata corect (obiectul np.array)
        if global_image == []:
            exception = Exception("Could not execute Wavelet Decomposition before Loading the image!")
            self.HandleBasicException(exception)
            return

        # functie care va afisa o imagine in fereastra coresp pana cand descompunerea se realizeaza
        self.VirtualProxy()

        # imaginea a fost incarcata corect si urmeaza sa extragem parametrii necesari executarii descompunerii
        decomposition_levels = int(self.decomposition_levels.text())
        DWT_type = str(self.DWT_type.currentText().lower())
        wavelet_type = defined_filters[self.wavelet_type.currentText().lower()]

        # determinam functia ce va fi folosita la descompunere, pe baza selectiei de pe interfata
        function = None
        if DWT_type == "pywavelets":
            function = LibraryDWTCompute
        elif DWT_type == "convolution - singlethread":
            function = SingleThread_ScratchDWTComputeRCWT
        elif DWT_type == "convolution - multithread":
            function = MultiThread_ScratchDWTComputeRCWT
        elif DWT_type == "linear-based - singlethread":
            function = SingleThread_ScratchDWTComputeLBWT
        elif DWT_type == "linear-based - multithread":
            function = MultiThread_ScratchDWTComputeLBWT

        # realizam descompunerea si masuram timpul de executie
        start = time.time_ns()
        wavelet_decomposition = WaveletMultipleDecomposition(global_image, wavelet_type, decomposition_levels, function)
        stop = time.time_ns()

        # obtinem imaginea de tip QPixmap necesara afisarii in interfata
        pixmapDWT = UI_Worker.ConvertNumpyImagetoPixmap(wavelet_decomposition)

        # setam imaginea pe interfata grafica
        width = self.wavelet_label.width()
        height = self.wavelet_label.height()
        self.wavelet_label.setPixmap(pixmapDWT.scaled(width, height, Qt.KeepAspectRatio))

        # odata ce am obtinut descompunerea, putem afisa parametrii corespunzatori
        self.wavelet_parameters.setVisible(True)

        # extragem parametrii imaginii rezultate si ii afisam pe interfata, adaugand, ca parametru, si timpul de executie
        qt_image_parameters = self.ExtractImageParameters(pixmapDWT)
        qt_image_parameters["width"] = int(qt_image_parameters["width"] / 2)
        qt_image_parameters["height"] = int(qt_image_parameters["height"] / 2)
        qt_image_parameters["time"] = (stop - start) / 1e9
        self.SetImageParameters([self.wavelet_width, self.wavelet_height, self.wavelet_size, self.wavelet_time],
                                qt_image_parameters)

    # functia de codificare cu ZeroTree si trimitere catre celalalt nod
    def ZeroTreeEncodingAndSend(self):
        global wavelet_decomposition
        global connection_established

        # in primul rand, aceasta functie nu poate fi apelata daca nu s-a generat lista de coeficienti (nu s-a efectuat DWT)
        # de asemenea, trebuie sa avem conexiunea stabilita pentru a putea trimite datele
        if wavelet_decomposition == []:
            exception = Exception("Could not execute ZeroTree Encoding and Sending before Loading the image "
                                  "and Makind the Wavelet Decomposition !")
            self.HandleBasicException(exception)
            return
        elif connection_established == False:
            exception = Exception("Could not execute ZeroTree Encoding and Sending before Establishing the connection!")
            self.HandleBasicException(exception)
            return

        # curatam consola de afisare a statusului!
        self.connection_status.clear()

        # trimitem toti parametrii necesari catre celalalt nod
        self.SendParameters()

        # extragem numarul de iteratii si nr. nivelelor de descompunere
        loops = self.loops.value()
        decomposition_levels = int(self.decomposition_levels.text())

        # extragem coordonatele dimensionale ale imaginii
        rows, cols = wavelet_decomposition.shape

        # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
        # de asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
        coefficients = ReorganizeMatrix(wavelet_decomposition, decomposition_levels)  # < 100 microsecunde

        # obtinem threshold-ul initial
        threshold = GetInitialThreshold(wavelet_decomposition)

        # determinam numarul de biti necesari encodarii fiecarei valori din lista de coeficienti
        # se are in vedere nr. de biti necesari pentru cea mai mare valoare
        nof_bites_needed = int(np.ceil(np.log2(np.max(wavelet_decomposition))))
        matrix_size = rows * cols * nof_bites_needed

        # curatam elemente de pe interfata ce vor afisa parametrii
        self.encoding_significance_map.clear()
        self.encoding_time.clear()
        self.encoding_reconstruction_values.clear()
        self.encoding_total.clear()
        self.encoding_difference.clear()
        self.encoding_compression.clear()
        self.encoding_current_iteration.clear()

        subordinateList = []
        for loop in range(loops):
            self.encoding_current_iteration.setText(str(loop + 1))
            self.encoding_current_iteration.repaint()
            start = time.time_ns()

            # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
            dominantList, coefficients = DominantPass(coefficients, (rows, cols), decomposition_levels,
                                                      int(threshold / np.power(2, loop)))

            # Extragem lista subordonata, care contine coeficientii care au fost determinati ca fiind significant in urma pasului dominant
            auxiliary = IdentifySignificants(dominantList)
            for aux in auxiliary:
                subordinateList.append(aux)

            dominantList_copy = np.copy(dominantList)

            # pastram doar valorile insignificante in dominantList, intrucat urmatorul pas dominant va parcurge doar aceste valori (insignificante)
            # dominantList contine valorile significante, care se afla si in subordonateList
            # asadar, pentru a determina valorile insignificante, facem diferenta celor doua liste
            dominantList = ListsDifference(dominantList, subordinateList)

            # efectuam pasul subordonat, in care toti coeficientii significant sunt encodati cu 0 si 1 avand in vedere pozitia in intervalul de incertitudine
            subordinateList = SubordinatePass(subordinateList, threshold, loop)

            # Observatie ! In mod obisnuit, dominantList_copy ar trebui sa contina valorile rezultate din pasul dominant (fara a tine cont de valorile
            # de reconstructie rezultate din pasul subordonat)
            # Insa, elementele significate cu valorile de reconstructie modificate rezultate din pasul subordonat sunt referinte la elementele din dominant List
            # de acelasi tip.
            # Asadar, cand se efectueaza pasul subordonat, valorile significante din dominantList_copy capata noile valori.
            # Din acest motiv, este suficient sa furnizam doar dominantList_copy, fara a furniza si valorile din subordonate List (se afla deja in dominantList_copy)
            sendList = GenerateSequenceToSend(dominantList_copy)

            # formatul listei de trimis [[significante_map_element, reconstruction_value]...]
            # extragem significance_map si lista valorilor de reconstructie pentru encodare si trimitere separata
            significance_map = list(map(lambda item: item[0], sendList))
            reconstruction_values = list(map(lambda item: item[1], sendList))

            # determinam conventiile de codificare a significance map (vor fi trimise inainte de imagine pentru ca decodorul sa stie cum sa interpreteze rezultatele)
            significance_map_encoding_conventions = SignificanceMapEncodingConventions()

            # codificam valorile de trimis astfel incat sa reducem nr. de biti necesari
            significance_map_encoding = SignificanceMapEncoding(significance_map, significance_map_encoding_conventions)

            # determinarea valorilor de 0 din lista de coeficienti se face pe baza significance map
            # asadar, eliminam coeficientii nuli din lista coeficientilor
            reconstruction_values = list(filter(lambda item: item != 0, reconstruction_values))

            stop = time.time_ns()
            self.encoding_time.setText(f"{(stop - start) / 1e9} s")

            # trimitem significance map si reconstruction values catre celalalt nod
            self.SendCoefficients(significance_map_encoding, reconstruction_values)

            # valorea maxima din significance_map este 3, care poate fi reprezentat pe 2 biti
            signif_map_bites_needed = 2
            reconstruction_values_bites_needed = int(np.ceil(np.log2(np.max(reconstruction_values))))
            len_items_to_send = len(significance_map_encoding) * signif_map_bites_needed + \
                                len(reconstruction_values) * reconstruction_values_bites_needed

            self.encoding_significance_map.setText(f"{BytestoKBytes(BitestoBytes(len(significance_map_encoding) * signif_map_bites_needed))} Kb")
            self.encoding_reconstruction_values.setText(f"{BytestoKBytes(BitestoBytes(len(reconstruction_values) * reconstruction_values_bites_needed))} Kb")
            self.encoding_total.setText(f"{BytestoKBytes(BitestoBytes(len_items_to_send))} Kb")
            self.encoding_difference.setText(f"{BytestoKBytes(BitestoBytes(matrix_size - len_items_to_send))} Kb")
            self.encoding_compression.setText(f"{round(matrix_size / len_items_to_send, 2)}")

        # semnalam finalizarea trimiterii tuturor datelor necesare
        self.SetConnectionStatus("* Trimitem mesajul de finalizare completa...")
        socketWRITEMessage(connection, "[finish]")

    # functie pentru trimiterea unor parametrii catre celalalt nod (numele imaginii, etc)
    def SendParameters(self):
        global connection

        # definim functia de trimitere a datelor prin socket
        def EncodeAndSend(printer,message, type):
            data_to_send = data_encode(f"[{type}] {message}")
            printer(f"Trimitem {type} : {message}")
            socketWRITE(connection, data_to_send)
            time.sleep(0.25)
            printer(f"{type} a fost trimis cu succes!")
            time.sleep(0.5)

        # trimitem numele imaginii
        filepath = self.image_source.toPlainText()
        filename = UI_Worker.ExtractFileName(filepath)
        EncodeAndSend(self.SetConnectionStatus,filename, "filename")

        # trimitem coordonatele dimensionale ale imaginii
        width = self.image_width.toPlainText()
        height = self.image_height.toPlainText()
        dimensions = f"{width} x {height}"
        EncodeAndSend(self.SetConnectionStatus,dimensions, "dimensions")

        # trimitem dimensiunea in kb a imaginii
        size = self.image_size.toPlainText()
        EncodeAndSend(self.SetConnectionStatus,size,  "size")

        # trimitem nr. nivelelor de descompunere
        dec_levels = self.decomposition_levels.text()
        EncodeAndSend(self.SetConnectionStatus,dec_levels, "decomposition_levels")

        # trimitem tipul de alg. folosit in descompunere
        alg_dwt_type = self.DWT_type.currentText()
        EncodeAndSend(self.SetConnectionStatus,alg_dwt_type, "decomposition_type")

        # trimitem tipul de wavelet folosit
        wavelet_type = self.wavelet_type.currentText()
        EncodeAndSend(self.SetConnectionStatus,wavelet_type, "wavelet_type")

        # trimitem nr. de iteratii
        loops = self.loops.text()
        EncodeAndSend(self.SetConnectionStatus,loops, "iteration_loops")

        # trimitem encodarea significance map
        signif_map_conventions = str(SignificanceMapEncodingConventions())
        EncodeAndSend(self.SetConnectionStatus, signif_map_conventions, "conventions")

    # functie pentru trimitea unor liste catre celalalt nod (significance map & reconstruction values)
    def SendCoefficients(self, significance_map, reconstruction_values):
        global connection

        # trimitem un mesaj de inceput pentru a delimita o noua iteratie
        self.SetConnectionStatus("* Trimitem mesajul de pornire")
        socketWRITEMessage(connection, "[start]")
        time.sleep(1)

        self.SetConnectionStatus("* Trimitem significance map")
        sig_map_str = str(significance_map).replace("[","").replace("]","").replace(" ","")
        socketWRITEMessage(connection, sig_map_str)
        time.sleep(1)

        self.SetConnectionStatus("* Trimitem delimitatorul")
        socketWRITEMessage(connection,"[delimitator]")
        time.sleep(1)

        self.SetConnectionStatus("* Trimitem reconstruction values")
        rec_vals_str = str(reconstruction_values).replace("[","").replace("]","").replace(" ","")
        socketWRITEMessage(connection, rec_vals_str)
        time.sleep(1)

        # trimitem mesajul de finalizare
        self.SetConnectionStatus("* Trimitem finalizatorul")
        socketWRITEMessage(connection, "[stop]")

    # functie pentru setarea label-ului ce descrie statusul conexiunii
    def SetConnectionStatus(self, text):
        # folosim un Lock, pentru sincronizare, in cazul folosirii mai multor threaduri care vor sa acceseze simultan resursa
        self.consoleLock.acquire()

        # adaugam textul si redesenam label-ul
        self.connection_status.setText(text)
        self.connection_status.repaint()

        # eliberam Lock-ul
        self.consoleLock.release()
        time.sleep(0.1)

    # functie care incearca conectarea cu celalalt nod
    # functia salveaza instanta conexiunii intr-un obiect global
    def CheckForConnections(self):
        global connection_established
        global sock
        global connection

        # verificare coresp celei de-a doua stari a butonului, cea de oprire a conexiunii
        if connection_established == True and connection != None:
            connection.close()
            sock.close()
            self.SetConnectionStatus("Conexiunea a fost inchisa cu succes...")
            return

        self.SetConnectionStatus("Se deschide socket-ul...")
        time.sleep(0.5)

        # AF-INET pentru familia de adrese IPv4
        # SOCK_STREAM pentru comunicare prin TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # setam posibilitatea de a refolosi o adresa deja folosita
        # pentru a preintampina o eroare care apare din cauza inchiderii fortate a conexiunii
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # asocierea socket-uui cu o interfata specifica de retea si un port
        sock.bind((config["host"], config["port"]))
        self.SetConnectionStatus("Socket-ul a fost deschis cu succes...")
        time.sleep(0.5)

        # asteptam conectarea unui client
        # apelam functia blocanta ce va returna conectiunea si adresa clientului
        self.SetConnectionStatus("Se asteapta clienti...")
        sock.listen()
        connection, address = sock.accept()

        # clientul este conectat si putem incepe comunicarea
        self.SetConnectionStatus(f"S-a conectat un client : \n{address}")

        # modificam butonul de realizare a conexiunii si setam flagul coresp.
        self.check_connections.setText("Stop connection")
        connection_established = True

        # identificam modalitatea de comunicare
        communicationMode = self.communication_mode.currentText()
        comSelection = 0 if "TCP" in communicationMode else 1 if "UART" in communicationMode else None

        # se va realiza un handshake pentru ca cele doua noduri sa convearga asupra aceleiasi modalitati de comunicare
        # - bucla infinita pentru a repeta handshake-ul, ori de cate ori este nevoie, pana se efectueaza cu succes
        while True:
            # informam clientul cu privire la alegerea facuta si realizam handshake-ul
            # salvam status-ul handshake-ului, conexiunea si tipul conexiunii
            type, conn, HSstatus = CommunicationHandshake(self.SetConnectionStatus, connection, comSelection)
            if not HSstatus:
                # handshake esuat
                self.SetConnectionStatus("* Handshake-ul a esuat!")
                time.sleep(0.5)
                self.SetConnectionStatus("* Se reia handshake-ul!")
            else:
                # handshake efectuat cu succes
                if type == 0:
                    # initiem comunicarea prin TCP
					# parasim bucla de reluare a handshake-ului, deoarece a fost efectuat cu succes
                    self.SetConnectionStatus("Handshake realizat cu succes!\nComunicare : TCP Sockets")
                    break
                elif type == 1:
                    # initiem comunicarea prin UART
					# parasim bucla de reluare a handshake-ului
                    self.SetConnectionStatus("Handshake realizat cu succes!\nComunicare : UART")
                    break
                else:
                    # tipul de comunicare identificat este eronat
					# reluam handshake-ul
                    self.SetConnectionStatus("* Canal de comunicare ales eronat!")

        self.SetConnectionStatus("Ready to send data...\n")


