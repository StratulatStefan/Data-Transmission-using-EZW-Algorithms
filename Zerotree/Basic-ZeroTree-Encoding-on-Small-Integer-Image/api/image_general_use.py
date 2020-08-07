from api.general_use import *

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

###########################################################################################

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