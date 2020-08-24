
from transmission_gui import *
from PySide2.QtGui import QImage
import numpy as np
import cv2 as cv

# - aceasta clasa contine anumite functii ale interfetei grafice, care nu au legatura directa cu obiectele
# interfetei grafice, ci cu anumite operatii prin care se genereaza obiectele interfetei (ex : conversii)
# - toate functiile acestei clase vor fi statice, pentru a nu instantia un obiect al clasei, ci doar
# pentru a folosi functiile ca atare
class UI_Worker:
    # functie care converteste un numpy.array intr-un obiect de tip pixmap
    # folosita pentru afisarea imaginii procesata in interfata grafica
    @staticmethod
    def ConvertNumpyImagetoPixmap(image):
        rows, cols = image.shape
        # valorile coeficientilor pot depasi intervalul de reprezentare 0-255.
        # astfel, coeficientii trebuie normalizati pentru a apartine intervalului specific Grayscale (0-255)
        img = np.copy(image)
        cv.normalize(src=image, dst=img, alpha=0, beta=255, norm_type=cv.NORM_MINMAX)

        img = np.require(img, np.uint8, 'C')
        img = QImage(img.data, cols, rows, cols, QImage.Format_Indexed8)

        return QPixmap.fromImage(img)

    # functie care converteste o imagine PixMap la grayscale
    @staticmethod
    def GrayScalePixMap(pixmap):
        # convertim pixmap-ul la formatul imagine
        image = QPixmap.toImage(pixmap)

        # convertim imaginea la grayscale
        grayscale = image.convertToFormat(QImage.Format_Grayscale8)

        # convertim imaginea grayscale la formatul pixmap
        return QPixmap.fromImage(grayscale)
