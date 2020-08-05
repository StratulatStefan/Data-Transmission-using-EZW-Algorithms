from api.wavelets import *
from api.zerotree import *
import time

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH, cv.IMREAD_GRAYSCALE)
    except Exception as exc:
        BasicException(exc)

    # facem descompunerea folosind wavelets
    try:
        # avem grija sa tratam exceptia generata din cauza tipului invalid de wavelet
        start = time.time_ns()
        print("----------Multi Thread Level 1----------")
        decomposition_level_1 = WaveletDecomposition(image, QMF_5_tap_symmetric, MultiThread_ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")
        print("----------------------------------------\n")

        start = time.time_ns()
        print("----------Multi Thread Level 2----------")
        decomposition_level_2 = WaveletDecomposition(decomposition_level_1['Aproximation LL'], QMF_5_tap_symmetric, MultiThread_ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")
        print("----------------------------------------\n")

        start = time.time_ns()
        print("----------Multi Thread Level 3----------")
        decomposition_level_3 = WaveletDecomposition(decomposition_level_2['Aproximation LL'], QMF_5_tap_symmetric, MultiThread_ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")
        print("----------------------------------------\n")
    except Exception as exc:
        BasicException(exc)

    # plotam rezultatele obtinute
    PlotDWT(decomposition_level_1, 0)
    PlotDWT(decomposition_level_2, 1)
    PlotDWT(decomposition_level_3, 2)

    pyplot.show()
