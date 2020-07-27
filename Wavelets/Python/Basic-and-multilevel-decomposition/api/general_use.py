import cv2 as cv
import numpy as np

##########################################################################################

# functie pentru citirea unei imagini
def ImageRead(path, color_schema):
    # primul parametru : sursa imaginii
    # al doilea parametru :  modul de citire (color/grayscale/etc)
    image = cv.imread(path, color_schema)
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

# functia care returneaza valorile unei imagini corespunzatoare unui anumit canal
def GetChannel(image, channel):
    if channel == 'r':
        return image[:,:,0]
    if channel == 'g':
        return image[:,:,1]
    if channel == 'b':
        return image[:,:,2]
    raise Exception(f"Invalid channel : {channel}!")

# functie pentru tratarea unei exceptii prin afisarea unui mesaj si inchiderea programului
def BasicException(exception):
    print(f"[Exception] {exception}")
    exit(-1)

# functie lambda care returneaza o cheie dintr-un dictionar dupa index
get_dict_key_by_index = lambda dict, index : list(dict.keys())[index]

# functie lambda care returneaza o valoare dintr-un dictionar dupa index
get_dict_value_by_index = lambda dict, index : dict[get_dict_key_by_index(dict, index)]