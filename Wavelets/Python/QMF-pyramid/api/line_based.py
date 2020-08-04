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
def Linear_Based(image, wavelet_type):
    # definim cele doua filtre si pastram doar primele n_dec decimale
    n_dec = 5
    low, high = map(lambda element : list(map(lambda item : round(item, n_dec), element)), wavelet_type)

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim vectorul rezultat
    temp = np.zeros(image.shape, np.float32)

    # dimensiunea filtrului
    if len(low) != len(high):
        raise Exception("Invalid filtering array size!")
    if len(low) % 2 == 1:
        low += [0]
        high += [0]
    filter_size = len(low)

    # cream un buffer in care vom stoca cele filter_size linii ce vor filtrare ulterior
    buffer = np.zeros((filter_size, cols), np.float32)

    # notal L = filter_size
    # filtram orizontal cate L linii
    # cand intalnim o a L-a linie, filtram vertical si anterioarele L linii
    pos = 0
    for i in range(0, rows):
        if i % filter_size == 0 and i != 0:
            for ii in range(0, int(filter_size / 2), 1):
                for j in range(0, cols, 1):
                    for index in range(filter_size):
                        # scalare
                        temp[pos + ii, j] += \
                            buffer[2 * ii + index if 2 * ii + index < filter_size else 2 * ii, j] * low[index]

                        # transformare
                        temp[pos + ii + int(rows / 2), j] += \
                            buffer[2 * ii + index if 2 * ii + index < filter_size else 2 * ii, j] * high[index]

            pos += int(filter_size / 2)

        # filtrare orizontala
        for j in range(0, int(cols / 2)):
            # scalare
            # functia de scalare (low) va genera jumatate din nr. total de valori, reprezentand valorile netezite
            # valorile acestei parcurgeri se pun in prima jumatate a vectorului rezultat
            buffer[i % filter_size, j] = image[i, 2 * j] * low[0]
            buffer[i % filter_size, j + int(cols / 2)] = image[i, 2 * j] * high[0]
            for index in range(1, filter_size):
                buffer[i % filter_size, j] += \
                    image[i, 2 * j + index if 2 * j + index < cols else 2 * j] * low[index]

                # transformare
                # functia de transformare (high) va genera jumatate din nr. total de valori, reprezentand detaliile
                # valorile acestei parcurgeri se pun in a doua jumatate a vectorului rezultat
                buffer[i % filter_size, j + int(cols / 2)] += \
                    image[i, 2 * j + index if 2 * j + index < cols else 2 * j] * high[index]

    return temp

