import pywt
import pywt.data
import numpy as np
from api.general_use import *


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

# functie care realizeaza compunerea canalelor individuale RGB pentru obtinerea unei singure reprezentari RGB
def RGBDWTRecompose(red_channel, green_channel, blue_channel):
    # - cele 4 descompuneri (LL, LH, HL, HH) au aceleasi caracteristici, deci cream un vector generic care sa ii defineasca
    # structura
    # obtinem coordonatele dimensionale
    rows, cols = next(iter(red_channel.values())).shape
    # cream vectorul generic
    generic = np.empty((rows, cols, 3), np.float32)
    # cream obiectul dictionar de acelasi tip ca cel specific DWT
    rgb_dwt = {}
    for subband_title in red_channel.keys():
        rgb_dwt.update({subband_title : np.copy(generic)})

    # compunerea celor 3 canale intr-un singur canal, pentru fiecare subbanda
    for index, subband in enumerate(rgb_dwt.values()):
        subband[:,:,0] = get_dict_value_by_index(red_channel, index)
        subband[:,:,1] = get_dict_value_by_index(green_channel, index)
        subband[:,:,2] = get_dict_value_by_index(blue_channel, index)
        if index == 0:
            cv.normalize(src=subband, dst=subband, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)

    return rgb_dwt