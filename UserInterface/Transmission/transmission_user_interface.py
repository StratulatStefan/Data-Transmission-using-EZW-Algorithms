'''
*   Mediul de dezvoltare QT genereaza interfata grafica sub forma unui fisier cu extensia ".ui" .
*   Asadar, pentru a obtine fisierul sursa python ce va contine codul interfetei grafice, vom folosi utilitarul
"pyside2-uic", care va primi ca input fisierul cu interfata de tip ".uic" si va avea ca output codul sursa de tip ".py"
*   Aceasta trebuie realizata inainte de a incarca codul sursa al interfetei in program si a-l utiliza.
'''

# inainte de a incarca codul sursa generat de QT, vom face conversia de la .ui la .py folosind pyside2-uic
import os

from PySide2.QtGui import QMovie

from api.wavelets import *
import time
os.system("pyside2-uic transmission.ui > transmission_gui.py")

# - am facut conversia interfetei la cod sursa; urmeaza, asadar, sa incarcam acest cod in programul principal si sa il
# utilizam
from transmission_gui import *
from worker import *

# definim un obiect global care va contine imaginea ce va fi incarcata din GUI
# acest obiect va fi folosit in prelucrarile ulterioare din algoritm
global_image = []

# definim obiectul global ce va contine descompunerea imaginii in coeficienti Wavelet
wavelet_decomposition = []

class GraphicalUserInterface(Ui_MainWindow):
    def __init__(self, window):
        self.setupUi(window)
        window.setFixedSize(window.size())
        self.ExtraObjectAttributes()

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
        url = url.replace("file:///", "")

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

        start = time.time_ns()
        # repara aici sa mearga descompunere multipla!!!
        wavelet_decomposition = WaveletMultipleDecomposition(global_image, wavelet_type, decomposition_levels, function)[0]
        stop = time.time_ns()

        rw, cl = list(map(lambda value : int(value/2), wavelet_decomposition.shape))

        # obtinem imaginea de tip QPixmap necesara afisarii in interfata
        pixmapDWT = UI_Worker.ConvertNumpyImagetoPixmap(wavelet_decomposition)

        width = self.wavelet_label.width()
        height = self.wavelet_label.height()
        self.wavelet_label.setPixmap(pixmapDWT.scaled(width, height, Qt.KeepAspectRatio))

        # odata ce am obtinut descompunerea, putem afisa parametrii corespunzatori
        self.wavelet_parameters.setVisible(True)

        qt_image_parameters = self.ExtractImageParameters(pixmapDWT)
        qt_image_parameters["width"] = int(qt_image_parameters["width"] / 2)
        qt_image_parameters["height"] = int(qt_image_parameters["height"] / 2)
        # adaugam ca parametru si timpul de descompunere
        qt_image_parameters["time"] = (stop - start) / 1e9
        self.SetImageParameters([self.wavelet_width, self.wavelet_height, self.wavelet_size, self.wavelet_time],
                                qt_image_parameters)

    # functie pentru incarcarea si afisarea imaginii
    def ImageLoadAndDisplay(self, path, image_label):
        # incarcam imaginea pentru afisare
        # vom folosi un obiect al librariei PySide2
        # (pentru prelucrarea imaginii, se va incarca folosind libraria OpenCV)
        qt_image = QPixmap(path)

        # verificam optiunea utilizatorului cu privire la spatiul de culoare al imaginii
        color_space_option = str(self.color_space.currentText())
        img = qt_image
        if color_space_option.lower() == "grayscale":
            # convertim imaginea la grayscale
            qt_image_grayscale = UI_Worker.GrayScalePixMap(qt_image)
            img = qt_image_grayscale

        # extragem o serie din parametrii imaginii
        qt_image_parameters = self.ExtractImageParameters(img)

        # obtinem dimensiunile label-ului
        width, height = self.image_label.width(), self.image_label.height()

        # afisam imaginea in elementul image_box si redimensionam label-ul astfel incat imaginea sa poata fi afisata complet
        image_label.setPixmap(img.scaled(width, height, Qt.KeepAspectRatio))

        # setam parametrii imaginii in box-ul coresp.
        self.SetImageParameters([self.image_width, self.image_height, self.image_size, self.image_bpp], qt_image_parameters)

    # functie pentru incarcarea imaginii intr-un obiect de tip numpy.array, pentru folosirea ulterioara in cadrul algoritmului
    def LoadNumpyImage(self, url):
        global global_image
        try:
            # verificam optiunea utilizatorului cu privire la spatiul de culoare al imaginii
            color_space_option = str(self.color_space.currentText())
            if color_space_option.lower() == "rgb":
                global_image = ImageRead(url, cv.IMREAD_COLOR)
            else:
                global_image = ImageRead(url, cv.IMREAD_GRAYSCALE)
        except Exception as exc:
            self.HandleBasicException(exc)

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

    # functie care se executa atunci cand o resursa nu este pregatita si nu vrem ca interfata sa se blocheze
    # folosita in cazul descompunerii
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

