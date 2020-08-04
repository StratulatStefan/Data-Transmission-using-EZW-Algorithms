from api.defined_filters import *
import threading

'''
-------------------------------
|        Convolutional         |
|             (or)             |
| Row-column wavelet transform |
-------------------------------

- The 2D DWT in divided into two 1D DWTs, namely horizontal and vertical filtering
- The horizontal processes the rows of the original image and stores the wavelet coefficients in an auxiliary matrix.
Thereafter, the vertical filtering phase processes the column of the aux matrix and stores the results back in the original matrix.
- Same complexity for each phase (horizontal and vertical)
- Different approaches to implement 2D DWT : 1). Convolution-based
'''

###########################################################################################################################
# mai multe filtre de acest tip se gasesc la : people.duke.edu/~hpgavin/SystemID/References/Liu-WaveletTransform-2010.pdf #
###########################################################################################################################

# functie care efectueaza descompunerea folosind RCWT, convolutie si Daubechies-4 wavelet
# avand in vedere ca efectuam convolutia pe o matrice de dimensiune mare (ex 512 x 512), calculul va dura foarte mult
# pentru a evita acest lucru, bucla for (de convolutie) va fi paralelizata (se cunoaste faptul ca datele nu depinde unele de altele).
# NU AM PARALELIZAT ! AM INCERCAT CATEVA SOLUTII BUNE, DAR NU AM CONCLUZIONAT !
def Convolutional(image, wavelet_type):
    # definim cele doua filtre
    low, high = wavelet_type

    # ne asiguram ca cele doua filtre au aceeasi dimensiune
    if len(low) != len(high):
        raise Exception("Invalid size for filters!")

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim vectorul auxiliar ce va contine rezultatele prelucrarilor
    temp = np.zeros(image.shape, np.float32)

    # definim un threadpool pentru executarea in paralel a buclei for
    # multiprocessing.cpu_count() : nr. max de thread-uri suportate de procesor

    # parcurgem imaginea pt aplicarea transf. de scalare (pe orizontala)
    for i in range(0, rows, 1):
        for j in range(0, int(cols/2), 1):
            # scalare
            # functia de scalare (low) va genera jumatate din nr. total de valori, reprezentand valorile netezite
            # valorile acestei parcurgeri se pun in prima jumatate a vectorului rezultat
            for index in range(0, len(low), 1):
                temp[i, j] += image[i, 2 * j + index if 2 * j + index < cols else 2 * j] * low[index]

                # transformare
                # functia de transformare (high) va genera jumatate din nr. total de valori, reprezentand detaliile
                # valorile acestei parcurgeri se pun in a doua jumatate a vectorului rezultat
                temp[i, j + int(cols / 2)] += image[i, 2 * j + index if 2 * j + index < cols else 2 * j] * high[index]

    temps = np.zeros(image.shape, np.float32)
    # parcurgem imaginea pt aplicarea transformarii (pe vertical)
    for i in range(0, int(rows/2), 1):
        for j in range(0, cols,1):
            # scalare
            for index in range(0, len(low), 1):
                temps[i, j] += temp[2 * i + index if 2 * i + index < rows else 2 * i, j] * low[index]

                # transformare
                temps[i + int(rows/2), j] += temp[2 * i + index if 2 * i + index < rows else 2 * i, j] * high[index]

    return temps

