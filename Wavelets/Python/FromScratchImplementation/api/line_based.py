from api.defined_filters import *
from api.general_use import *

'''
-------------------------------
| Line-based wavelet transform |
-------------------------------

- The vertical filtering starts as soon as a sufficient number of lines, as determine by the filter length, has been
horizontally filtered.
- First, the horizontal filtering filters L rows, where L is the filter length, and stores the low-pass and high-pass values
interleaved in an L x M buffer.
- There, the columns of this small buffer are filtered.
- This produces two wavelet coefficients rows, which are stored in different subbands in an auxiliary matrix.
- Finally, these stages are repeated to process all rows and cols
'''

###########################################################################################################################
# mai multe filtre de acest tip se gasesc la : people.duke.edu/~hpgavin/SystemID/References/Liu-WaveletTransform-2010.pdf #
###########################################################################################################################

# functie care efectueaza descompunerea folosind LBWT, Daubechies-4 wavelet
def Linear_Based_Daubechies_4(image):
    # definim cele doua filtre si pastram doar primele n_dec decimale
    n_dec = 5
    low, high = map(lambda element : list(map(lambda item : round(item, n_dec), element)), Daubechies_4())

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim vectorul rezultat
    temp = np.empty(image.shape, np.float32)

    # dimensiunea filtrului
    if len(low) != len(high):
        raise Exception("Invalid filtering array size!")
    filter_size = len(low)

    # cream un buffer in care vom stoca cele filter_size linii ce vor filtrare ulterior
    buffer = np.zeros((filter_size, cols), np.float32)

    # notal L = filter_size
    # filtram orizontal cate L linii
    # cand intalnim o a L-a linie, filtram vertical si anterioarele L linii
    pos = 0
    for i in range(0, rows, 1):
        if i % filter_size == 0 and i != 0:
            for ii in range(0, int(filter_size / 2), 1):
                for j in range(0, cols, 1):
                    # scalare
                    temp[pos + ii, j] = buffer[2 * ii, j] * low[0] + \
                                   buffer[2 * ii + 1 if 2 * ii + 1 < filter_size else 2 * ii, j] * low[1] + \
                                   buffer[2 * ii + 2 if 2 * ii + 2 < filter_size else 2 * ii, j] * low[2] + \
                                   buffer[2 * ii + 3 if 2 * ii + 3 < filter_size else 2 * ii, j] * low[3]
                    # transformare
                    temp[pos + ii + int(rows / 2), j] = buffer[2 * ii, j] * high[0] + \
                                                   buffer[2 * ii + 1 if 2 * ii + 1 < filter_size else 2 * ii, j] * high[1] + \
                                                   buffer[2 * ii + 2 if 2 * ii + 2 < filter_size else 2 * ii, j] * high[2] + \
                                                   buffer[2 * ii + 3 if 2 * ii + 3 < filter_size else 2 * ii, j] * high[3]
            pos += int(filter_size/2)
        # filtrare orizontala
        for j in range(0, int(cols / 2) - 1, 1):
            # scalare
            # functia de scalare (low) va genera jumatate din nr. total de valori, reprezentand valorile netezite
            # valorile acestei parcurgeri se pun in prima jumatate a vectorului rezultat
            buffer[i % filter_size, j] = image[i, 2 * j + 0] * low[0] + \
                                                       image[i, 2 * j + 1] * low[1] + \
                                                       image[i, 2 * j + 2] * low[2] + \
                                                       image[i, 2 * j + 3] * low[3]
            # transformare
            # functia de transformare (high) va genera jumatate din nr. total de valori, reprezentand detaliile
            # valorile acestei parcurgeri se pun in a doua jumatate a vectorului rezultat
            buffer[i % filter_size, j + int(cols / 2)] = image[i, 2 * j + 0] * high[0] + \
                                                                         image[i, 2 * j + 1] * high[1] + \
                                                                         image[i, 2 * j + 2] * high[2] + \
                                                                         image[i, 2 * j + 3] * high[3]

    return temp

