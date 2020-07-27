from api.general_use import *
from api.plotter import *
from api.wavelets import *

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH)
    except Exception as exc:
        print(f"[Exception] {exc}")
        exit(-1)
    #######################################################################
    # facem descompunerea folosind wavelets
    # pentru determinarea principalelor tipuri de wavelet : pywt.wavelist()
    decomposition = WaveletDecomposition(image, "haar") # descompunere cu un singur nivel
    try:
        # descompunere pe mai nivele
        # avem grija sa tratam exceptia generata din cauza unui nr. invalid de nivele
        multiple_decomposition = WaveletMultipleDecomposition(image, "haar", 1)
    except Exception as e:
        print(f"[Exception] {e}")
        exit(-1)
    #######################################################################
    # obtinem o singura imagine care contine cele 4 cadre
    DWT = DWTResultComposer(decomposition)
    #######################################################################
    # plotam rezultatele obtinute
    pyplot.figure(0)
    Plot(image, 111, "Original image")
    PlotDWT(decomposition, 1)
    PlotMultiDWT(multiple_decomposition, 0)
    pyplot.show()
