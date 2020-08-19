from api.zerotree import *
from api.image_general_use import *
from api.wavelets import *
import time
from api.plotter import *
from api.decoder import *
from api.encoder import *

# acest script nu are ca scop observarea de rezultate vizuale in termeni de imagini, ci doar de valori
# avem ca input o imagine mica (8x8) asupra careia s-a aplicat DWT pe 3 nivele
# dorim sa realizam encodarea folosind Successive-Approximation Quantization, prezentata in documentul principal
# avand la baza un exemplu prezentat in document, ne asteptam sa obtinem aceleasi rezultate

# repara SendEncoding


if __name__ == "__main__":
    DWT = np.array(([63,   -34,    49,    10,     7,    13,   -12,     7],
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

    # setam nr. nivelelor de descompunere
    decomposition_levels = 1

    #imagePATH = "D:\Confidential\EZW Algorithm\lena.png"
    #imagePATH = "D:\Confidential\EZW Algorithm\saga.jpg"
    imagePATH = "D:\Confidential\EZW Algorithm\\tree.jpg"

    try:
        image = ImageRead(imagePATH, cv.IMREAD_GRAYSCALE)
    except Exception as exc:
        BasicException(exc)

    print("-------------------------------------------------")
    print(f"Dimensiune imagine originala : {int(image.shape[0])} x {int(image.shape[1])}")

    # schimba formula aici!
    if image.shape[0] / np.power(2,decomposition_levels) <= 4:
        raise Exception("Too much decomposition levels!")

    if decomposition_levels == 1:
        LL, (HL, LH, HH) = pywt.dwt2(image, "haar")
        DWT = np.zeros(image.shape, np.float32)
    else:
        for i in range(decomposition_levels):
            LL, (HL, LH, HH) = pywt.dwt2(image, "haar")
            if i == decomposition_levels - 2:
                DWT = np.zeros(LL.shape, np.float32)
            image = LL
    r, c = LL.shape
    DWT[:r, :c] = LL
    DWT[:r, c:] = HL
    DWT[r:, :c] = LH
    DWT[r:, c:] = HH
    transmission_DWT = pywt.idwt2((LL, (HL, LH, HH)), "haar")
    Plot(transmission_DWT, 251, "Transmission Recomposed")
    Plot(DWT,252,"Transmission DWT")

    # extragem coordonatele dimensionale ale imaginii
    rows, cols = DWT.shape

    loops = 5

    print(f"Nivele de descompunere : {decomposition_levels}")
    print(f"Iteratii de aplicare a threshold-ului : {loops}")
    print("-------------------------------------------------\n\n")

    nof_bites_needed = int(np.ceil(np.log2(np.max(DWT))))
    matrix_size = rows * cols * nof_bites_needed
    print(f"Matricea de coeficienti contine {BytestoKBytes(BitestoBytes(matrix_size)) } Kb")

    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # de asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    coefficients = ReorganizeMatrix(DWT, decomposition_levels) # < 100 microsecunde

    threshold = GetInitialThreshold(DWT)

    subordinateList = []
    total_time = 0
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    for loop in range(loops):
        # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
        dominantList, coefficients = DominantPass(coefficients, (rows, cols), decomposition_levels,int(threshold / np.power(2, loop)))

        # Extragem lista subordonata, care contine coeficientii care au fost determinati ca fiind significant in urma pasului dominant
        auxiliary = IdentifySignificants(dominantList)
        for aux in auxiliary:
            subordinateList.append(aux)

        dominantList_copy = np.copy(dominantList)

        # pastram doar valorile insignificante in dominantList, intrucat urmatorul pas dominant va parcurge doar aceste valori (insignificante)
        # dominantList contine valorile significante, care se afla si in subordonateList
        # asadar, pentru a determina valorile insignificante, facem diferenta celor doua liste
        dominantList = ListsDifference(dominantList, subordinateList)

        # efectuam pasul subordonat, in care toti coeficientii significant sunt encodati cu 0 si 1 avand in vedere pozitia in intervalul de incertitudine
        subordinateList = SubordinatePass(subordinateList, threshold, loop)

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

        signif_map_bites_needed = 3
        reconstruction_values_bites_needed = int(np.ceil(np.log2(np.max(reconstruction_values))))
        len_items_to_send = len(significance_map_encoding) * signif_map_bites_needed + \
                            len(reconstruction_values) * reconstruction_values_bites_needed
        print(f"Significance Map ({BytestoKBytes(BitestoBytes(len(significance_map_encoding) * signif_map_bites_needed))} Kb) + "
              f"Reconstruction Values : ({BytestoKBytes(BitestoBytes(len(reconstruction_values) * reconstruction_values_bites_needed ))} Kb) = "
              f"{BytestoKBytes(BitestoBytes(len_items_to_send))} Kb")
        print(f"Diferenta (biti castigati) : {BytestoKBytes(BitestoBytes(matrix_size - len_items_to_send))} Kb")
        print(f"Raport compresie : {round(matrix_size / len_items_to_send,2)}")
        print("#######################################################")

        # trimitem significance_map si valorile de recontructie catre decoder
        # (ar trebui sa trimitem catre celalalt RPi, dar momentam, aceasta functie doar va recompune lista de coeficienti)
        #print(significance_map)
        send = SendEncodings(decomposition_levels, DWT.shape, significance_map_encoding_conventions, significance_map_encoding,reconstruction_values)
        msg = f"Loop {loop + 1}" if loop + 1 < loops else "Reception DWT"
        Plot(send, int(f"25{3 + loop}"), msg)

    r,c = send.shape
    r = int(r/2)
    c = int(c/2)
    LL = send[:r,:c]
    HL = send[:r, c:]
    LH = send[r:, :c]
    HH = send[r:, c:]
    coeffs = (LL, (HL, LH, HH))
    img = pywt.idwt2(coeffs,"haar")
    Plot(img, int(f"25{3 + loops}"), "Recomposed")

    pyplot.show()

