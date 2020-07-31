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
        #decomposition = WaveletDecomposition(image, "db4", LibraryDWTCompute) # descompunere cu un singur nivel
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition1 = None
        #decomposition1 = WaveletDecomposition(image, "db4", ScratchDWTComputeRCWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition2 = None
        #decomposition2 = WaveletDecomposition(image, "db4", ScratchDWTComputeLBWT)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        start = time.time_ns()
        decomposition3 = WaveletDecomposition(image, "db4", ScratchDWTComputeLS)
        stop = time.time_ns()
        print(f"Timpul necesar ex : {(stop - start) / 1e9} s")

        # descompunere pe mai nivele
        # avem grija sa tratam exceptia generata din cauza unui nr. invalid de nivele
        multiple_decomposition = WaveletMultipleDecomposition(image, "haar", 1, LibraryDWTCompute)
    except Exception as exc:
        BasicException(exc)

    #######################################################################
    # obtinem o singura imagine care contine cele 4 cadre
    #DWT = DWTResultComposer(decomposition)
    #######################################################################

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
    #PlotMultiDWT(multiple_decomposition, 0)
    ###############################################################################################
    ####################################### RGB image #############################################
    '''
    # citim imaginea
    try:
        image = ImageRead(imagePATH, cv.IMREAD_COLOR)
    except Exception as exc:
        BasicException(exc)

    #######################################################################
    # descompunerea folosind DWT trebuie sa se faca pe fiecare canal (R,G,B) in parte
    # obtinem cele 3 canale corespunzatoare imaginii RGB
    try:
        # nu uitam sa tratam exceptia coresp. canalului invalid specificat
        red_channel   = GetChannel(image,'r')
        green_channel = GetChannel(image,'g')
        blue_channel = GetChannel(image, 'b')
    except Exception as exc:
        BasicException(exc)
    # realizam descompunerea haar pe fiecare subcanal
    wavelet_type = 'db1'
    red_channel_DWT = WaveletDecomposition(red_channel, wavelet_type)
    green_channel_DWT = WaveletDecomposition(green_channel, wavelet_type)
    blue_channel_DWT = WaveletDecomposition(blue_channel, wavelet_type)
    # recompunem cele trei rezultate obtinute pentru a obtine o imagine RGB
    rgb_dwt = RGBDWTRecompose(red_channel_DWT, green_channel_DWT, blue_channel_DWT)
    #######################################################################
    # plotam rezultatele obtinute
    pyplot.figure(1)
    # functia imshow din libraria pyplot deseneaza imaginile in format BGR, deci trebuie sa facem conversia
    Plot(cv.cvtColor(image, cv.COLOR_RGB2BGR),111, "Original image")
    # convertim cele 4 subbenzi la BGR
    for value in rgb_dwt.values():
        cv.cvtColor(src=value, dst=value, code=cv.COLOR_RGB2BGR)
    PlotDWT(rgb_dwt, 2)
    '''
    pyplot.show()
