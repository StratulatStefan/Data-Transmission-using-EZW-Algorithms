from api.zerotree import *
from matplotlib import pyplot
import time

# acest script nu are ca scop observarea de rezultate vizuale in termeni de imagini, ci doar de valori
# avem ca input o imagine mica (8x8) asupra careia s-a aplicat DWT pe 3 nivele
# dorim sa realizam encodarea folosind Successive-Approximation Quantization, prezentata in documentul principal
# avand la baza un exemplu prezentat in document, ne asteptam sa obtinem aceleasi rezultate


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
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = DWT.shape
    decomposition_levels = int(math.log(rows * cols, 4))


    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # de asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    start = time.perf_counter_ns()
    coefficients = ReorganizeMatrix(DWT, decomposition_levels) # < 100 microsecunde
    stop = time.perf_counter_ns()
    print(f"Timp in microsecunde : {(stop - start) / 1e3}")

    threshold = GetInitialThreshold(DWT)

    loops = 3
    subordinateList = []
    for loop in range(loops):
        # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
        dominantList, coefficients = DominantPass(coefficients, (rows, cols), decomposition_levels, int(threshold / np.power(2, loop)))

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

        # trimitem significance_map si valorile de recontructie catre decoder
        # (ar trebui sa trimitem catre celalalt RPi, dar momentam, aceasta functie doar va recompune lista de coeficienti)
        print(significance_map)
        x = SendEncodings(DWT.shape,significance_map_encoding_conventions, significance_map_encoding, reconstruction_values)
        print("#############################################")
        '''
        print(f"Loop {loop + 1}")
        printList(subordinateList)
        print("xxxxxx")
        printList(dominantList)
        print("\n\n")
        '''
    pyplot.show()

