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
    # definim cele doua filtre
    low, high = Daubechies_4()

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim vectorul rezultat
    temp = np.empty(image.shape, np.float32)

    # dimensiunea filtrului
    if len(low) != len(high):
        raise Exception("Invalid filtering array size!")
    filter_size = len(low)

    # cream un buffer in care vom stoca cele filter_size linii ce vor filtrare ulterior
    buffer = np.empty((filter_size, cols), np.float32)

    # filtram orizontal cate filter_size linii
    # cand intalnim o a-"filter-size" linie, filtram vertical si anterioarele filter_size linii
    for i in range(0, rows, 1):
        if i % filter_size == 0:
            # o a filter-size linie; efectuam filtrarea verticala
            if i != 0:
                # filtram anterioarele 4 linii
                for ii in range(0, int(filter_size / 2) - 1, 1):
                    for j in range(0, cols , 1):
                        # scalare
                        temp[i + ii, j] = buffer[2 * ii, j] * low[0] + \
                                  buffer[2 * ii + 1, j] * low[1] + \
                                  buffer[2 * ii + 2, j] * low[2] + \
                                  buffer[2 * ii + 3, j] * low[3]
                        # transformare
                        temp[i + ii + int(rows / 2), j] = buffer[2 * ii, j] * high[0] + \
                                                  buffer[2 * ii + 1, j] * high[1] + \
                                                  buffer[2 * ii + 2, j] * high[2] + \
                                                  buffer[2 * ii + 3, j] * high[3]
            # golim bufferul in care vom stoca cele 4 linii
            buffer = np.empty((filter_size, cols), np.float32)
        # filtrare orizontala
        for j in range(0, int(cols / 2) - 1, 1):
            # scalare
            # functia de scalare (low) va genera jumatate din nr. total de valori, reprezentand valorile netezite
            # valorile acestei parcurgeri se pun in prima jumatate a vectorului rezultat
            buffer[i % 4, j % 4] = image[i, 2 * j + 0] * low[0] + \
                             image[i, 2 * j + 1] * low[1] + \
                             image[i, 2 * j + 2] * low[2] + \
                             image[i, 2 * j + 3] * low[3]
            # transformare
            # functia de transformare (high) va genera jumatate din nr. total de valori, reprezentand detaliile
            # valorile acestei parcurgeri se pun in a doua jumatate a vectorului rezultat
            buffer[i % 4, (j + int(cols / 2)) % 4] = image[i, 2 * j + 0] * high[0] + \
                                             image[i, 2 * j + 1] * high[1] + \
                                             image[i, 2 * j + 2] * high[2] + \
                                             image[i, 2 * j + 3] * high[3]

    return temp

