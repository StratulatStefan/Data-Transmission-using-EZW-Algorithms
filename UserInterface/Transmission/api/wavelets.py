import pywt.data
from api.convolutional import *
from api.line_based import *
from api.defined_filters import available_wavelets
import multiprocessing
from functools import partial
from api.image_general_use import *

# functie care realizeaza descompunerea cu wavelets, folosind functia din libraria PyWavelets
def LibraryDWTCompute(image, wavelet_type):
    return pywt.dwt2(image, wavelet_type)

# functie care realizeaza descompunerea cu wavelets, folosind propria implementare si
# abordarea Row-Column Wavelet Transform
def SingleThread_ScratchDWTComputeRCWT(image, wavelet_type):
    if wavelet_type in available_wavelets:
        tmp = Convolutional(wavelet_type(), image)
    else:
        raise Exception("Invalid wavelet type!")
    rows, cols = map(lambda x : int(x/2), tmp.shape)
    LL = tmp[:rows, :cols]
    HL = tmp[:rows, cols:]
    LH = tmp[rows:, :cols]
    HH = tmp[rows:, cols:]
    return LL, (LH, HL, HH)

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

# functie care realizeaza descompunerea cu wavelets, folosind propria implementare si
# abordarea Row-Column Wavelet Transform
def SingleThread_ScratchDWTComputeLBWT(image, wavelet_type):
    if wavelet_type in available_wavelets:
        tmp = Linear_Based(wavelet_type(), image)
    else:
        raise Exception("Invalid wavelet type!")
    rows, cols = map(lambda x : int(x/2), tmp.shape)
    LL = tmp[:rows, :cols]
    HL = tmp[:rows, cols:]
    LH = tmp[rows:, :cols]
    HH = tmp[rows:, cols:]
    return LL, (LH, HL, HH)

# functie care realizeaza descompunerea cu wavelets, folosind propria implementare si
# abordarea Row-Column Wavelet Transform
def MultiThread_ScratchDWTComputeLBWT(image, wavelet_type):
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
        func = partial(Linear_Based, wavelet_type())
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
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # definim coordonatele imaginii rezultate din transformare
    wrows, wcols = list(map(lambda value : int(value / 2), [rows, cols]))

    result = np.zeros((rows, cols), np.float32)

    # realizam descompunerea imaginii folosind tipul de wavelet dat ca parametru
    LL, (LH, HL, HH) = function(image, wavelet_type)
    result[:wrows, :wcols] = LL
    result[:wrows, wcols:] = HL
    result[wrows:, :wcols] = LH
    result[wrows:, wcols:] = HH
    return result

# functie care realizeaza descompunere multipla in subbenzi
def WaveletMultipleDecomposition(image, wavelet_type, level, function):
    if level <= 0:
        raise Exception("Invalid decomposition level!")

    LL = np.copy(image)
    rows, cols = image.shape
    final_result = None
    while level > 0:
        decomposition = WaveletDecomposition(LL, wavelet_type, function)
        try:
            final_result[:rows, :cols] = decomposition
        except Exception:
            final_result = np.copy(decomposition)
        rows = int(rows/2)
        cols = int(cols/2)
        LL = decomposition[:rows, :cols]
        level -= 1

    return final_result