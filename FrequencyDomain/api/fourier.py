import cv2 as cv
import numpy as np

####################################################################################################

# Functie care realizeaza recentrarea spectrului in mijlocul imaginii, astfel incat sa poata fi interpretat corect.
# Schimbam originea, din  (0,0) in centrul imaginii
# Toata aceasta functie putea fi substituiata cu apelul : np.fft.fftshift(dft)
def RecenterSpectrum(mag):
    # realizam o copie profunda a parametrului, pentru a nu-i schimba valoarea
    magnitude = np.copy(mag)

    # extragem nr. de linii si de coloane ale imaginii (widh si height)
    magRows, magCols = magnitude.shape[0], magnitude.shape[1]

    # noul centrul
    cx = int(magRows / 2)
    cy = int(magCols / 2)

    ####################
    #   q0   #   q1    #
    #        #         #
    ####################
    #   q2   #    q3   #
    #        #         #
    ####################
    q0 = magnitude[0:cx, 0:cy]
    q1 = magnitude[cx:cx + cx, 0:cy]
    q2 = magnitude[0:cx, cy:cy + cy]
    q3 = magnitude[cx:cx + cx, cy:cy + cy]

    ####################
    #   q3   #   q1    #
    #        #         #
    ####################
    #   q2   #    q0   #
    #        #         #
    ####################
    tmp = np.copy(q0)
    magnitude[0:cx, 0:cy] = q3
    magnitude[cx:cx + cx, cy:cy + cy] = tmp

    ####################
    #   q3   #   q2    #
    #        #         #
    ####################
    #   q1   #    q0   #
    #        #         #
    ####################
    tmp = np.copy(q1)
    magnitude[cx:cx + cx, 0:cy] = q2
    magnitude[0:cx, cy:cy + cy] = tmp

    return magnitude

####################################################################################################

# functie care realizeaza calculul transformatei Fourier
def Fourier(image):
    # convertim valorile pixelilor, de la uint8 la float32, intrucat valorile rezultate din calcul sunt in virgula
    # mobila si avem nevoie de precizie
    floatimage = np.float32(image)

    # DFT_COMPLEX_OUTPUT : rezultatul sa fie complex (vector de perechi de forma [Re(DFT), Img(DFT)] )
    dft = cv.dft(floatimage, flags=cv.DFT_COMPLEX_OUTPUT)

    # recentram spectrul, astfel incat sa aiba originea in mijlocul imaginii
    dft_shifted = np.fft.fftshift(dft)

    # Sau putem folosi ft_shifted = RecenterSpectrum(dft)

    return dft_shifted

####################################################################################################

# functie care realizeaza calculul transformatei Fourier inverse
def InverseFourier(dft):
    # recentram spectrul (din mijlocul imaginii) in origine (0,0)
    f_ishift = np.fft.fftshift(dft)

    # Sau putem folosi f_ishift = RecenterSpectrum(dft)

    # realizam calculul tr. Fourier inverse
    idft = cv.idft(f_ishift)
    # SAU cv.dft(f_ishift, flags=cv.DFT_INVERSE)

    return idft

####################################################################################################

# functie care realizeaza calculul magnitudinii spectrului tr. Fourier
def Magnitude(dft):
    # rezultatul tr. Fourier este complex, de forma array([Real(DFT), Img(DFT)], ...)
    # asadar, spargem vectorul DFT in 2 vectori, ce contin partea reala si partea imaginara
    [Re, Im] = cv.split(dft)

    #                                                                  _________________
    # realizam calculul magnitudinii, pe baza formulei : Magnitude = \/ Re ^ 2 + Img ^ 2
    magnitude = cv.sqrt(cv.pow(Re,2) + cv.pow(Im, 2))

    # Sau putem folosi direct functia opencv : magnitude = cv.magnitude(Re, Im)
    return magnitude

####################################################################################################

# functie care realizeaza trecerea magnitudinii la scara logaritmica
def LogScale(magnitude):
    # Trecem la scara logaritmica intrucat avem unele valori foarte mari, sau foarte mici pe care nu le putem observa
    # Trebuie sa le aducem intr-un interval, in care sa poata fi interpretate corect (0-255)
    # Valorile foarte mari vor fi albe, iar cele foarte mici, vor fi negre
    # Formula : Magnitudine = log(1 + Magnitudine)
    matofOnes = np.ones(magnitude.shape, magnitude.dtype)
    magnitude = cv.add(matofOnes, magnitude)
    magnitude = cv.log(magnitude)

    # Sau putem folosi direct functia opencv : cv.log(magnitude[:] + 1)
    return magnitude

####################################################################################################

