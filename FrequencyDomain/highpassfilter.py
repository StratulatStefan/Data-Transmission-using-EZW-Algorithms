from api.plotter import *
from api.fourier import *
from api.plotter import *
from api.general_use import *

# functie care creeaza un filtru trece-sus patract
# size  : dimensiunea filtrului (ex : 512,512)
# level : frecventa de taiere
def HighPassFilterSquare(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.ones((rows, cols, 2), np.uint8)
    mask[crow - level:crow + level, ccol - level:ccol + level] = 0
    return mask

###############################################################################

# functie care creeaza un filtru trece-sus ideal
# size  : dimensiunea filtrului (ex : 512,512)
# level : frecventa de taiere
def HighPassFilterIdeal(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.ones((rows, cols, 2), np.uint8)

    # - restrangem cautarea la un patrat de latura = level, deoarece incadreaza perfect cercul
    # eliminam astfel parcurgerea unor valori fara sens
    for cr in range(crow - level, crow + level):
        for cl in range(ccol - level, ccol + level):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            if distance < level:
                mask[cr, cl] = 0

    return mask

###############################################################################

# functie care creeaza un filtru trece-sus Butterworth
# size  : dimensiunea filtrului
# level : frecventa de taiere
# grade : gradul filtrului
def HighPassFilterButterWorth(size, level, grade):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)


    # valorile filtrului trebuie sa fie valori reale, avand in vedere ca
    # ecuatia filtrului contine o impartire
    mask = np.float32(mask)

    # valorile filtrului trebuie sa fie valori reale, avand in vedere ca
    # ecuatia filtrului contine o impartire
    mask = np.float32(mask)

    for cr in range(rows):
        for cl in range(cols):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            if distance != 0:
                mask[cr, cl] = np.power(1 + np.power(level / distance, 2 * grade),-1)

    return mask

###############################################################################

# functie care creeaza un filtru trece-sus Gaussian
# size  : dimensiunea filtrului
# level : frecventa de taiere
def HighPassFilterGaussian(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)

    # valorile filtrului trebuie sa fie valori reale, avand in vedere ca
    # ecuatia filtrului contine o impartire
    mask = np.float32(mask)

    for cr in range(rows):
        for cl in range(cols):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            mask[cr, cl] = 1 - np.exp(-np.power(distance,2) / (2 * np.power(level,2)))

    return mask


if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH)
    except Exception as exc:
        print(f"[Exception] {exc}")
        exit(-1)

    #####################################################

    lowpass15 = HighPassFilterGaussian(image.shape, 15)
    lowpass30 = HighPassFilterGaussian(image.shape, 30)
    lowpass50 = HighPassFilterGaussian(image.shape, 50)
    lowpass65 = HighPassFilterGaussian(image.shape, 65)

    '''
    lowpass15 = HighPassFilterButterWorth(image.shape, 15, 2)
    lowpass30 = HighPassFilterButterWorth(image.shape, 30, 2)
    lowpass50 = HighPassFilterButterWorth(image.shape, 50, 2)
    lowpass65 = HighPassFilterButterWorth(image.shape, 65, 2)
    '''

    '''
    lowpass15 = HighPassFilterIdeal(image.shape, 15)
    lowpass30 = HighPassFilterIdeal(image.shape, 30)
    lowpass50 = HighPassFilterIdeal(image.shape, 50)
    lowpass65 = HighPassFilterIdeal(image.shape, 65)
    '''
    '''
    lowpass15 = HighPassFilterSquare(image.shape, 15)
    lowpass30 = HighPassFilterSquare(image.shape, 30)
    lowpass50 = HighPassFilterSquare(image.shape, 50)
    lowpass65 = HighPassFilterSquare(image.shape, 65)
    '''

    #####################################################
    fourier = Fourier(image)
    fourier15 = fourier * lowpass15
    fourier30 = fourier * lowpass30
    fourier50 = fourier * lowpass50
    fourier65 = fourier * lowpass65

    spectrum_fourier = LogScale(Magnitude(fourier))
    spectrum_highpass15 = LogScale(Magnitude(fourier15))
    spectrum_highpass30 = LogScale(Magnitude(fourier30))
    spectrum_highpass50 = LogScale(Magnitude(fourier50))
    spectrum_highpass65 = LogScale(Magnitude(fourier65))

    img_back_15 = Magnitude(InverseFourier(fourier15))
    img_back_30 = Magnitude(InverseFourier(fourier30))
    img_back_50 = Magnitude(InverseFourier(fourier50))
    img_back_65 = Magnitude(InverseFourier(fourier65))
    #####################################################
    pyplot.figure(0)
    Plot(image, 121, "Original")
    Plot(spectrum_fourier, 122, "Fourier")
    pyplot.figure(1)
    Plot(spectrum_highpass15, 241,"High Pass Fourier 15")
    Plot(img_back_15, 242, "Original with High Pass 15")
    Plot(spectrum_highpass30, 243,"Low High Fourier 30")
    Plot(img_back_30, 244, "Original with High Pass 30")
    Plot(spectrum_highpass50, 245,"High Pass Fourier 50")
    Plot(img_back_50, 246, "Original with High Pass  50")
    Plot(spectrum_highpass65, 247,"High Pass Fourier 65")
    Plot(img_back_65, 248, "Original with High Pass  65")
    pyplot.show()