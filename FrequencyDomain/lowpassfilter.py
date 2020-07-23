from api.plotter import *
from api.fourier import *
from api.general_use import *

# functie care creeaza un filtru trece-jos patrat
# size  : dimensiunea filtrului (ex : 512,512)
# level : frecventa de taiere
def LowPassFilterSquare(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)
    mask[crow - level:crow + level, ccol - level:ccol + level] = 1
    return mask

###############################################################################

# functie care creeaza un filtru trece-jos ideal
# size  : dimensiunea filtrului (ex : 512,512)
# level : frecventa de taiere
def LowPassFilterIdeal(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)

    # - restrangem cautarea la un patrat de latura = level, deoarece incadreaza perfect cercul
    # eliminam astfel parcurgerea unor valori fara sens
    for cr in range(crow - level, crow + level):
        for cl in range(ccol - level, ccol + level):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            if distance < level:
                mask[cr, cl] = 1

    return mask

###############################################################################

# functie care creeaza un filtru trece-jos Butterworth
# size  : dimensiunea filtrului
# level : frecventa de taiere
# grade : gradul filtrului
def LowPassFilterButterWorth(size, level, grade):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)

    # valorile filtrului trebuie sa fie valori reale, avand in vedere ca
    # ecuatia filtrului contine o impartire
    mask = np.float32(mask)

    for cr in range(rows):
        for cl in range(cols):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            mask[cr, cl] = np.power(1 + np.power(distance / level,2 * grade),-1)

    return mask

###############################################################################

# functie care creeaza un filtru trece-jos Gaussian
# size  : dimensiunea filtrului
# level : frecventa de taiere
def LowPassFilterGaussian(size, level):
    rows, cols = size
    crow, ccol = int(rows / 2), int(cols / 2)

    mask = np.zeros((rows, cols, 2), np.uint8)

    # valorile filtrului trebuie sa fie valori reale, avand in vedere ca
    # ecuatia filtrului contine o impartire
    mask = np.float32(mask)

    for cr in range(rows):
        for cl in range(cols):
            distance = np.sqrt(np.power(cr - crow, 2) + np.power(cl - ccol,2))
            mask[cr, cl] = np.exp(-np.power(distance,2) / (2 * np.power(level,2)))

    return mask

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH)
    except Exception as exc:
        print(f"[Exception] {exc}")
        exit(-1)

    #############################################

    lowpass15 = LowPassFilterGaussian(image.shape, 15)
    lowpass30 = LowPassFilterGaussian(image.shape, 30)
    lowpass50 = LowPassFilterGaussian(image.shape, 50)
    lowpass65 = LowPassFilterGaussian(image.shape, 65)

    '''
    lowpass15 = LowPassFilterButterWorth(image.shape, 15, 2)
    lowpass30 = LowPassFilterButterWorth(image.shape, 30, 2)
    lowpass50 = LowPassFilterButterWorth(image.shape, 50, 2)
    lowpass65 = LowPassFilterButterWorth(image.shape, 65, 2)
    '''

    '''
    lowpass15 = LowPassFilterIdeal(image.shape, 15)
    lowpass30 = LowPassFilterIdeal(image.shape, 30)
    lowpass50 = LowPassFilterIdeal(image.shape, 50)
    lowpass65 = LowPassFilterIdeal(image.shape, 165)
    '''
    '''
    lowpass15 = LowPassFilterSquare(image.shape, 15)
    lowpass30 = LowPassFilterSquare(image.shape, 30)
    lowpass50 = LowPassFilterSquare(image.shape, 50)
    lowpass65 = LowPassFilterSquare(image.shape, 65)
    '''
    #############################################
    fourier = Fourier(image)
    fourier15 = fourier * lowpass15
    fourier30 = fourier * lowpass30
    fourier50 = fourier * lowpass50
    fourier65 = fourier * lowpass65

    spectrum_fourier = LogScale(Magnitude(fourier))
    spectrum_lowpass15 = LogScale(Magnitude(fourier15))
    spectrum_lowpass30 = LogScale(Magnitude(fourier30))
    spectrum_lowpass50 = LogScale(Magnitude(fourier50))
    spectrum_lowpass65 = LogScale(Magnitude(fourier65))

    img_back_15 = Magnitude(InverseFourier(fourier15))
    img_back_30 = Magnitude(InverseFourier(fourier30))
    img_back_50 = Magnitude(InverseFourier(fourier50))
    img_back_65 = Magnitude(InverseFourier(fourier65))
    #############################################
    pyplot.figure(0)
    Plot(image, 121, "Original")
    Plot(spectrum_fourier, 122, "Fourier")
    pyplot.figure(1)
    Plot(spectrum_lowpass15, 241, "Low Pass Fourier 15")
    Plot(img_back_15, 242, "Original with Low Pass 15")
    Plot(spectrum_lowpass30, 243, "Low Pass Fourier 30")
    Plot(img_back_30, 244, "Original with Low Pass 30")
    Plot(spectrum_lowpass50, 245, "Low Pass Fourier 50")
    Plot(img_back_50, 246, "Original with Low Pass  50")
    Plot(spectrum_lowpass65, 247, "Low Pass Fourier 65")
    Plot(img_back_65, 248, "Original with Low Pass  65")
    pyplot.show()