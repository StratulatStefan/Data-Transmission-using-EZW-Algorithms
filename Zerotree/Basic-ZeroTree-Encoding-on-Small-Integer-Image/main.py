from api.zerotree import *
from api.image_general_use import *
from api.wavelets import *
import time
from api.plotter import *


# acest script nu are ca scop observarea de rezultate vizuale in termeni de imagini, ci doar de valori
# avem ca input o imagine mica (8x8) asupra careia s-a aplicat DWT pe 3 nivele
# dorim sa realizam encodarea folosind Successive-Approximation Quantization, prezentata in documentul principal
# avand la baza un exemplu prezentat in document, ne asteptam sa obtinem aceleasi rezultate

# repara SendEncoding


if __name__ == "__main__":
    DWTs = np.array(([63,   -34,    49,    10,     7,    13,   -12,     7],
                   [-31,    23,    14,   -13,     3,     4,     6,    -1],
                   [ 15,    14,     3,   -12,     5,    -7,     3,     9],
                   [ -9,    -7,   -14,     8,     4,    -2,     3,     2],
                   [ -5,     9,    -1,    47,     4,     6,    -2,     2],
                   [  3,     0,    -3,     2,     3,    -2,     0,     4],
                   [  2,    -3,     6,    -4,     3,     6,     3,     6],
                   [  5,    11,     5,     6,     0,     3,    -4,     4]), np.int32)

    DWTs = np.array(([26,    6,   13,   10],
                    [-7,    7,    6,    4],
                    [ 4,   -4,    4,   -3],
                    [ 2,   -2,   -2,    0]), np.int32)

    DWTs = np.array(([63, -34, 49, 10, 7,13, -12,7,8,21,5,4,7,-2,3,1],
                    [-31,23,14,-13,3,4,6,-1,4,1,3,2,-5,4,2,3],
                    [15,14,3,-12,5,-7,3,9,3,-1,4,2,6,8,11,5],
                    [-9,-7,-14,8,4,-2,3,2,4,11,5,-8,-4,3,4,6],
                    [-5,9,-1,47,4,6,-2,2,8,-2,9,-5,1,3,8,2],
                    [3,0,-3,2,3,-2,0,4,3,0,2,1,4,5,8,-1],
                    [2,-3,6,-4,3,6,3,6,2,1,3,-1,5,2,6,3],
                    [5,11,5,6,0,3,-4,4,1,-5,6,8,-9,10,4,5],
                    [3,3,-2,3,9,11,4,8,1,-5,6,1,5,1,10,6],
                    [6,4,8,1,1,15,5,9,2,3,3,6,-2,1,12,4],
                    [11,15,2,33,-1,13,3,7,0,8,5,0,-1,2,1,2],
                    [4,6,-2,8,7,18,-3,-7,1,7,4,-10,6,1,3,2],
                    [0,1,1,2,8,16,8,1,5,11,-2,-12,4,3,8,3],
                    [2,-6,4,1,2,-1,7,-2,9,15,-8,-1,8,6,5,1],
                    [3,1,8,9,5,2,9,7,-2,-5,-1,6,9,6,-1,-2],
                    [-2,2,3,-6,-3,3,4,1,1,-8,2,4,12,3,2,3]), np.int32)

    #imagePATH = "D:\Confidential\EZW Algorithm\lena.png"
    imagePATH = "D:\Confidential\EZW Algorithm\saga.jpg"
    try:
        image = ImageRead(imagePATH, cv.IMREAD_GRAYSCALE)
    except Exception as exc:
        BasicException(exc)
    
    LL, (HL, LH, HH) = pywt.dwt2(image, "haar")
    DWT = np.zeros(LL.shape, np.float32)
    LL, (HL, LH, HH) = pywt.dwt2(LL, "haar")
    r, c = LL.shape
    DWT[:r, :c] = LL
    DWT[:r, c:] = HL
    DWT[r:, :c] = LH
    DWT[r:, c:] = HH
    Plot(image, 221, "img")
    Plot(DWT,222,"adasda")

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = DWT.shape

    # setam nr. nivelelor de descompunere
    decomposition_levels = 2

    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # de asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    start = time.perf_counter_ns()
    coefficients = ReorganizeMatrix(DWT, decomposition_levels) # < 100 microsecunde
    stop = time.perf_counter_ns()
    print(f"Timp in secunde pentru transformare in lista de coeficienti: {(stop - start) / 1e9} s")

    threshold = GetInitialThreshold(DWT)

    loops = 5
    subordinateList = []
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    for loop in range(loops):
        # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
        start = time.perf_counter_ns()
        dominantList, coefficients = DominantPass(coefficients, (rows, cols), decomposition_levels,int(threshold / np.power(2, loop)))
        stop = time.perf_counter_ns()
        print(f"Timp in secunde Dominant Pass : {(stop - start) / 1e9} s")


        # Extragem lista subordonata, care contine coeficientii care au fost determinati ca fiind significant in urma pasului dominant
        auxiliary = IdentifySignificants(dominantList)
        for aux in auxiliary:
            subordinateList.append(aux)

        dominantList_copy = np.copy(dominantList)

        # pastram doar valorile insignificante in dominantList, intrucat urmatorul pas dominant va parcurge doar aceste valori (insignificante)
        # dominantList contine valorile significante, care se afla si in subordonateList
        # asadar, pentru a determina valorile insignificante, facem diferenta celor doua liste
        start = time.perf_counter_ns()
        dominantList = ListsDifference(dominantList, subordinateList)
        stop = time.perf_counter_ns()
        print(f"Timp in secunde ListDifference : {(stop - start) / 1e9} s")

        # efectuam pasul subordonat, in care toti coeficientii significant sunt encodati cu 0 si 1 avand in vedere pozitia in intervalul de incertitudine
        start = time.perf_counter_ns()
        subordinateList = SubordinatePass(subordinateList, threshold, loop)
        stop = time.perf_counter_ns()
        print(f"Timp in secunde Subordinate Pass : {(stop - start) / 1e9} s")

        # Observatie ! In mod obisnuit, dominantList_copy ar trebui sa contina valorile rezultate din pasul dominant (fara a tine cont de valorile
        # de reconstructie rezultate din pasul subordonat)
        # Insa, elementele significate cu valorile de reconstructie modificate rezultate din pasul subordonat sunt referinte la elementele din dominant List
        # de acelasi tip.
        # Asadar, cand se efectueaza pasul subordonat, valorile significante din dominantList_copy capata noile valori.
        # Din acest motiv, este suficient sa furnizam doar dominantList_copy, fara a furniza si valorile din subordonate List (se afla deja in dominantList_copy)
        sendList = GenerateSequenceToSend(dominantList_copy)

        # formatul listei de trimis [[significante_map_element, reconstruction_value]...]
        # extragem significance_map si lista valorilor de reconstructie pentru encodare si trimitere separata
        significance_map =  list(map(lambda item : item[0], sendList))
        reconstruction_values = list(map(lambda item : item[1], sendList))

        # determinam conventiile de codificare a significance map (vor fi trimise inainte de imagine pentru ca decodorul sa stie cum sa interpreteze rezultatele)
        significance_map_encoding_conventions = SignificanceMapEncodingConventions()

        # codificam valorile de trimis astfel incat sa reducem nr. de biti necesari
        significance_map_encoding = SignificanceMapEncoding(significance_map, significance_map_encoding_conventions)

        # determinarea valorilor de 0 din lista de coeficienti se face pe baza significance map
        # asadar, eliminam coeficientii nuli din lista coeficientilor
        reconstruction_values = list(filter(lambda item : item != 0, reconstruction_values))

        # trimitem significance_map si valorile de recontructie catre decoder
        # (ar trebui sa trimitem catre celalalt RPi, dar momentam, aceasta functie doar va recompune lista de coeficienti)
        #print(significance_map)
        start = time.perf_counter_ns()
        send = SendEncodings(decomposition_levels, DWT.shape, significance_map_encoding_conventions, significance_map_encoding,reconstruction_values)
        stop = time.perf_counter_ns()
        print(f"Timp in secunde trimitere si recompunere : {(stop - start) / 1e9} s")
        #print(send)
        print("#############################################")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    Plot(send,223,"asdasda")
    r,c = send.shape
    r = int(r/2)
    c = int(c/2)
    LL = send[:r,:c]
    HL = send[:r, c:]
    LH = send[r:, :c]
    HH = send[r:, c:]
    coeffs = (LL, (HL, LH, HH))
    img = pywt.idwt2(coeffs,"haar")
    Plot(img, 224,"ssss")
    pyplot.show()

