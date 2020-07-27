import cv2 as cv
import numpy as np

##########################################################################################

# functie pentru citirea unei imagini
def ImageRead(path):
    # primul parametru : sursa imaginii
    # al doilea parametru :  modul de citire (color/grayscale/etc)
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)
    # functia de citire nu returneaza exceptie daca path nu este corect, ci doar None
    if not isinstance(image, np.ndarray):
        # imposibilitatea de citire a img. se detecteaza la prima folosire a imaginii, cand
        # observam ca aceasta nu apartine tipului numpy.ndarray.
        # In acest caz, aruncam o exceptie.
        raise Exception("Imaginea nu a putut fi citita!")
    # imaginea a fost citita corect

    # OpenCV citeste imaginile RGB ca vectori multidimensional de tip numpy arrays, doar ca IN ORDINE INVERSA
    # adica in format BGR.
    # pentru a putea folosi imaginile in format corect, trebuie sa facem conversia la RGB
    return image

##########################################################################################

# functie care realizeaza redimensionarea imaginii
# image : imaginea
# dimensions : parametrii de scalare {fx, fy} (dictionar)
def ImageResize(image, dimensions):
    return cv.resize(image, None, fx=dimensions['fx'], fy = dimensions['fy'])