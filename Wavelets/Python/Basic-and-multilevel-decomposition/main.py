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

    # pentru determinarea principalelor tipuri de wavelet : pywt.wavelist()
    print(pywt.wavelist())
    decomposition = WaveletDecomposition(image, "bior1.1")
    DWT = DWTResultComposer(decomposition)
    mDWT = WaveletMultipleDecomposition(image, "haar", 3)
    PlotMultiDWT(mDWT, 0)

    #pyplot.figure(0)
    #Plot(image, 111, "Original image")

    #PlotDWT(decomposition, 1)


    pyplot.show()
