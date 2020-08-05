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

##########################################################################################

# functie pentru tratarea unei exceptii prin afisarea unui mesaj si inchiderea programului
def BasicException(exception):
    print(f"[Exception] {exception}")
    exit(-1)

# functie lambda care returneaza o cheie dintr-un dictionar dupa index
get_dict_key_by_index = lambda dict, index : list(dict.keys())[index]

# functie lambda care returneaza o valoare dintr-un dictionar dupa index
get_dict_value_by_index = lambda dict, index : dict[get_dict_key_by_index(dict, index)]

##########################################################################################

# functie care descompune imaginea in "counter" subimagini dupa linii
# cu alte cuvinte, imaginea se va imparti in "counter" bucati pe linii
########################       ########################         ########################
# aaaaaaaaaaaaaaaaaaaa #       # aaaaaaaaaaaaaaaaaaaa #         # cccccccccccccccccccc #
# bbbbbbbbbbbbbbbbbbbb #       ########################         ########################
# cccccccccccccccccccc #   =>                                                                   (6 subimagini)
# dddddddddddddddddddd #       ########################
# eeeeeeeeeeeeeeeeeeee #       # bbbbbbbbbbbbbbbbbbbb #         ......................
# ffffffffffffffffffff #       ########################
########################
def ImageDecompose(image, counter):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim dimensiunea in linii a subimaginii
    block = int(rows / counter)

    # construim un template pentru fiecare subimagine in parte
    # dimensiuni : (image.rows / counter ) x image.cols
    template = np.zeros((block, cols), np.float32)

    # definim vectorul de subimagini
    subimages = []

    # realizam "counter" iteratii in care impartim imaginea in subimagini
    for index in range(counter):
        # definim subimaginea pe baza template-ului
        subimage = np.copy(template)

        # extragem subimaginea corespunzatoare indexului curent
        subimage = image[block * index: block * (index + 1), :]

        # adaugam imaginea la vectorul de subimagini
        subimages.append(subimage)

    return subimages

##########################################################################################

# functie care recompune imaginea din "counter" subimagini dupa linii
def ImageRecompose(images):
    # extragem numarul de subimagini
    nof_subimages = len(images)

    # definim coordonatele dimensionale ale imaginii finale
    subimg_rows, subimg_cols = images[0].shape
    rows = nof_subimages * subimg_rows
    cols = subimg_cols

    #definim imaginea finala
    image = np.zeros((rows, cols), np.float32)

    # parcurgem cele "nof_subimages" si recompunem imaginea finala
    for index, subimage in enumerate(images):
        rws, cls = map(lambda x: int(x / 2), subimage.shape)
        LL = subimage[:rws, :cls]
        HL = subimage[:rws, cls:]
        LH = subimage[rws:, :cls]
        HH = subimage[rws:, cls:]
        image[index * int(subimg_rows/2) : (index + 1) * int(subimg_rows/2), : int(subimg_cols/2)] = LL
        image[index * int(subimg_rows/2) : (index + 1) * int(subimg_rows/2), int(subimg_cols/2) : ] = HL
        image[index * int(subimg_rows/2) + int(rows/2) : (index + 1) * int(subimg_rows/2) + int(rows/2), : int(subimg_cols/2)] = LH
        image[index * int(subimg_rows/2) + int(rows/2) : (index + 1) * int(subimg_rows/2) + int(rows/2), int(subimg_cols/2) : ] = HH
    return image

##########################################################################################

# - functie care determina numarul ideal de procese care vor executa paralel functiile dorite
# - acest numar trebuie sa fie cat mai aproape de 10 : s-a observat experimental ca cele mai bune rezultate (timp)
# se obtin atunci cand nr. de procese este cat mai apropiat de 10
# - totodata, acest numar de procese trebuie sa fie divizor al coordonatei dimensionale pe baza careia se face divizarea (size)
def GetIdealProcessesNumber(size):
    ideal = 10

    # tratam cazul cel mai frecvent
    if size % 8 == 0:
        return 8

    # divizorii unui numar se gasesc pana la jumatatea acestuia
    half = int(size/2)

    # determinam divizorii numarului
    dividers = []
    for index in range(1, half):
        if size % index == 0:
            dividers.append(index)

    # determinam divizorul cel mai apropiat de "ideal"
    if ideal in dividers:
        return ideal

    # determinam diferenta in modul dintre fiecare divizor si 10
    candidates = list(map(lambda value : abs(value - 10), dividers))

    # indexul diferentei celei mai mici reprezinta indexul elementului cel mai apropiat de 10
    indexOfIdeal = candidates.index(min(candidates))
    ideal = dividers[indexOfIdeal]
    return ideal
