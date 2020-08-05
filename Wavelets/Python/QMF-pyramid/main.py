from api.general_use import *
from api.plotter import *
from api.wavelets import *
import time

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    ####################################### grayscale image #######################################
    # citim imaginea
    try:
        image = ImageRead(imagePATH, cv.IMREAD_GRAYSCALE)
    except Exception as exc:
        BasicException(exc)
    #######################################################################
    # facem descompunerea folosind wavelets
    # pentru determinarea principalelor tipuri de wavelet : pywt.wavelist()
    try:
        # avem grija sa tratam exceptia generata din cauza tipului invalid de wavelet

        start = time.time_ns()
        decomposition = None
        #decomposition = WaveletDecomposition(image, "db2", LibraryDWTCompute) # descompunere cu un singur nivel
        stop = time.time_ns()
        #print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition2 = None
        print("----------Multi Thread----------")
        #decomposition2 = WaveletDecomposition(image, QMF_5_tap_symmetric, MultiThread_ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition1 = None
        print("----------Single Thread----------")
        #decomposition1 = WaveletDecomposition(image, QMF_5_tap_symmetric, SingleThread_ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition4 = None
        print("----------Multi Thread----------")
        decomposition4 = WaveletDecomposition(image, QMF_5_tap_symmetric, MultiThread_ScratchDWTComputeLBWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition3 = None
        print("----------Single Thread----------")
        decomposition3 = WaveletDecomposition(image, QMF_5_tap_symmetric, SingleThread_ScratchDWTComputeLBWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")
    except Exception as exc:
        BasicException(exc)

    # plotam rezultatele obtinute
    #pyplot.figure(0)
    #Plot(image, 111, "Original image")
    if decomposition:
        PlotDWT(decomposition, 0)
    if decomposition1:
       PlotDWT(decomposition1, 1)
    if decomposition2:
        PlotDWT(decomposition2, 2)
    if decomposition3:
        PlotDWT(decomposition3, 3)
    if decomposition4:
        PlotDWT(decomposition4, 4)
    pyplot.show()
