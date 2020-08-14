import pywt.data
from api.convolutional import *
from api.defined_filters import available_wavelets
import multiprocessing
from functools import partial
from api.plotter import *

# functie care realizeaza descompunerea cu wavelets, folosind functia din libraria PyWavelets
def LibraryDWTCompute(image, wavelet_type):
    return pywt.dwt2(image, wavelet_type)


# functie care realizeaza descompunerea cu wavelets, folosind propria implementare si
# abordarea Row-Column Wavelet Transform
def MultiThread_ScratchDWTComputeRCWT(image, wavelet_type):
    if wavelet_type not in available_wavelets:
        raise Exception("Invalid wavelet type!")

    # convolutia va fi executata de "processes" procese
    # trebuie sa fie divizor al dimensiunii imaginii si sa fie cat mai aproape de 10
    processes = GetIdealProcessesNumber(image.shape[0])

    # descompunem imaginea in "processes" subimagini, fiecare subimagine urmand sa fie executata de catre un proces
    # exemplu : imagine 512 x 512 si 8 subprocese => 8 imagini de 64 x 512 asupra carora se face convolutia in paralel
    # descompunerea se face pe linii
    images = ImageDecompose(image, processes)

    # definim Pool-ul de procese care vor executa functia in paralel
    with multiprocessing.Pool(processes=processes) as pool:
        # executam operatia de convolutie in paralel, asupra celor "processes" imagini si extragem rezultatul final
        func = partial(Convolutional, wavelet_type())
        tmp = pool.map(func=func, iterable=images)


    final = ImageRecompose(tmp)
    rows, cols = map(lambda x : int(x/2), final.shape)
    LL = final[:rows, :cols]
    HL = final[:rows, cols:]
    LH = final[rows:, :cols]
    HH = final[rows:, cols:]
    return LL, (LH, HL, HH)

# functie care realizeaza descompunerea imaginii folosind wavelets
# LL, LH, HL, HH
def WaveletDecomposition(image, wavelet_type, function):
    titles = ["Aproximation LL",
              "Horizontal Details HL",
              "Vertical Details LH",
              "Diagonal Details HH"]

    # realizam descompunerea imaginii folosind wavelet-ul Daubechies
    #LL, (LH, HL, HH) = LibraryDWTCompute(image, wavelet_type)
    LL, (LH, HL, HH) = function(image, wavelet_type)

    # compunem dictionarul ce contine obiectele rezultate si titlul
    output = {
        titles[0] : LL,
        titles[1] : LH,
        titles[2] : HL,
        titles[3] : HH
    }
    return output

# functie care realizeaza descompunere multipla in subbenzi
def WaveletMultipleDecomposition(image, wavelet_type, level, function):
    if level <= 0:
        raise Exception("Invalid decomposition level!")

    DWT = {}
    LL = np.copy(image)
    initial_level = np.copy(level)
    while level > 0:
        decomposition = WaveletDecomposition(LL, wavelet_type, function)
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