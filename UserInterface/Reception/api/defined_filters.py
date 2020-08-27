from api.general_use import *
import pywt.data

# functie care creeaza filtrele low si high corespunzatoare QMF pyramid n-tap
# are ca input coeficientii filtrului low pass
# formeaza filtrul low pass si high in formatul [hn-1, hn-2, .., h1, h0, h1, ... hn-2, hn-1]
def CreateQMFPyramidFilter(*low):
    lows = list(low)
    lows.reverse()
    lows = lows[:-1] +  list(low)

    high = list(map(lambda index: np.power(-1, index) * lows[index], range(len(lows))))
    return lows, high

def QMF_13_tap_symmetric():
    h0 =  0.77371
    h1 =  0.42995
    h2 = -0.05783
    h3 = -0.09800
    h4 = 0.03905
    h5 = 0.02165
    h6 = -0.01456

    return CreateQMFPyramidFilter(h0, h1, h2, h3, h4, h5, h6)

def QMF_9_tap_symmetric():
    h0 =  0.56458
    h1 =  0.29271
    h2 = -0.05224
    h3 = -0.04271
    h4 =  0.01995

    return CreateQMFPyramidFilter(h0, h1, h2, h3, h4)

def QMF_7_tap_symmetric():
    h0 =  0.603553
    h1 =  0.255251
    h2 = -0.051776
    h3 = -0.005251

    return CreateQMFPyramidFilter(h0, h1, h2, h3)

def QMF_5_tap_symmetric():
    h0 =  0.60762
    h1 =  0.25000
    h2 = -0.05381

    arr = CreateQMFPyramidFilter(h0, h1, h2)
    arr[0].reverse()
    arr[1].reverse()
    return arr

def Daubechies_4():
    h0 = (1 + np.sqrt(3)) / (4 * np.sqrt(2))
    h1 = (3 + np.sqrt(3)) / (4 * np.sqrt(2))
    h2 = (3 - np.sqrt(3)) / (4 * np.sqrt(2))
    h3 = (1 - np.sqrt(3)) / (4 * np.sqrt(2))

    g0 = h3
    g1 = -h2
    g2 = h1
    g3 = -h0

    high = [g3, g2, g1, g0]
    low = [h3, h2, h1, h0]

    return low, high

available_wavelets = [Daubechies_4,
                      QMF_13_tap_symmetric,
                      QMF_9_tap_symmetric,
                      QMF_7_tap_symmetric,
                      QMF_5_tap_symmetric]

defined_filters = {"haar" : "haar",
                   "biorthogonal": "bior1.1",
                   "daubechies-1" : "db1",
                   "daubechies" : Daubechies_4,
                   "5-tap qmf pyramid" : QMF_5_tap_symmetric,
                   "9-tap qmf pyramid" : QMF_9_tap_symmetric}