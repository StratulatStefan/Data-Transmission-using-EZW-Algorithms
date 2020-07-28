from api.general_use import *

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
