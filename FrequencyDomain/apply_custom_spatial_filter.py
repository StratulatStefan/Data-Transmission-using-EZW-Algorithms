from api.fourier import *
from api.general_use import *
from api.plotter import *

# functie care creeaza un filtru spatial Gaussian 5x5
def GaussianSpacialFilter():
    ####################
    # 1   4   6   4  1 #
    # 4  16  24  16  4 #
    # 6  24  36  24  6 #
    # 4  16  24  16  4 #
    # 1   4   6   4  1 #
    ####################
    array = np.array([[1,  4,  6,  4, 1],
                     [4, 16, 24, 16, 4],
                     [6, 24, 36, 24, 6],
                     [4, 16, 24, 16, 4],
                     [1,  4,  6,  4, 1]])

    return array[:] # / 256

# - functie care realizeaza extinderea unui vector
# - functia este folosita pentru aplicarea unui filtru spatial pe o anumita imagine
# aplicarea filtrului in domeniul spatial se face prin convolutie, iar in domeniul frecventa se face prin
# simpla inmultire; asadar, pentru a putea realiza inmultirea, trebuie ca cele doua (DFT(imagine) si DFT(filtru))
# sa aiba aceeasi dimensiune; asadar, aducem filtrul la dimensinea imaginii
def ExpandArray(array, new_size):
    # determinam nr. de linii si coloane ptr. imagine si pt filtru
    new_rows, new_cols = new_size
    rhalf, chalf = int(new_rows / 2), int(new_cols / 2)
    rows, cols = int(array.shape[0] / 2), int(array.shape[1] / 2)

    # definim un array de zerouri de aceeasi dimensiune cu imaginea originala
    new_array = np.zeros((new_rows, new_cols), np.float32)

    # filtrul va fi scris in new_array, fiind centrat in mijlocul vectorului
    # exemplu:
    ###################################
    # 0   0   0   0   0   0  0  0  0  #
    # 0   0   0   0   0   0  0  0  0  #
    # 0   0   1   4   6   4  1  0  0  #
    # 0   0   4  16  24  16  4  0  0  #
    # 0   0   6  24  36  24  6  0  0  #
    # 0   0   4  16  24  16  4  0  0  #
    # 0   0   1   4   6   4  1  0  0  #
    # 0   0   0   0   0   0  0  0  0  #
    # 0   0   0   0   0   0  0  0  0  #
    ###################################
    new_array[rhalf - rows : rhalf + rows + 1, chalf - cols : chalf + cols + 1] = array

    return new_array

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH)
    except Exception as exc:
        print(f"[Exception] {exc}")
        exit(-1)

    #############################################
    # definim un filtru gaussian de 5x5 in domeniul spatial
    gaussian_spacial = GaussianSpacialFilter()
    # realizam expandarea filtrului la dim. imaginii pentru a putea efectua inmultirea
    gaussian_spacial = ExpandArray(gaussian_spacial, image.shape)

    # determinam tr. Fourier a imaginii
    image_fourier = Fourier(image)
    # determinam tr. Fourier a acestui filtru
    gaussian_fourier = Fourier(gaussian_spacial)

    # realizam inmultirea celor doua in sensul aplicarii filtrului
    image_filtered = image_fourier * gaussian_fourier

    # determinam magnitudinea spectrului imaginii initiale
    image_spectrum = LogScale(Magnitude(image_fourier))
    # determinam magnitudinea filtrului expandat
    expanded_filter_spectrum = LogScale(Magnitude(gaussian_fourier))
    # determinam magnitudinea spectrului rezultat
    image_filtered_spectrum = LogScale(Magnitude(image_filtered))

    # determinam imaginea rezultata prin aplicarea inversa a tr. Fourier
    resultat = Magnitude(InverseFourier(image_filtered))


    # realizam desenare
    Plot(image, 241, "Original")
    Plot(image_spectrum, 242, "Spectrul rezultat al imaginii")
    Plot(expanded_filter_spectrum, 245, "Filtru in frecventa")
    Plot(image_filtered_spectrum, 246, "Spectrul rezultat dupa filtrare")
    Plot(resultat, 247, "Rezultat")
    pyplot.show()