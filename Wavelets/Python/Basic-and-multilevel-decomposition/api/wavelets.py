import pywt
import pywt.data
import numpy as np


# functie care realizeaza descompunerea imaginii folosind wavelets
# LL, LH, HL, HH
def WaveletDecomposition(image, wavelet_type):
    titles = ["Aproximation LL",
              "Horizontal Details HL",
              "Vertical Details LH",
              "Diagonal Details HH"]

    # realizam descompunerea imaginii folosind wavelet-ul Daubechies
    LL, (LH, HL, HH) = pywt.dwt2(image, wavelet_type)

    # compunem dictionarul ce contine obiectele rezultate si titlul
    output = {
        titles[0] : LL,
        titles[1] : LH,
        titles[2] : HL,
        titles[3] : HH
    }
    return output


# functie care realizeaza descompunere multipla in subbenzi
def WaveletMultipleDecomposition(image, wavelet_type, level):
    if level <= 0:
        raise Exception("Invalid decomposition level!")

    DWT = {}
    LL = np.copy(image)
    initial_level = np.copy(level)
    while level > 0:
        decomposition = WaveletDecomposition(LL, wavelet_type)
        DWT[initial_level - level + 1] = decomposition
        LL = decomposition["Aproximation LL"]
        level -= 1
    return DWT