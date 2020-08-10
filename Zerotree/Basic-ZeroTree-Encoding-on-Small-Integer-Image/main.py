from api.zerotree import *
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


    # extragem coordonatele dimensionale ale imaginii
    rows, cols = DWT.shape

    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # de asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    start = time.perf_counter_ns()
    coefficients = ReorganizeMatrix(DWT, 3) # < 100 microsecunde
    stop = time.perf_counter_ns()
    print(f"Timp in microsecunde : {(stop - start) / 1e3}")

    T0 = GetInitialThreshold(DWT)

    # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
    dominantList, coefficients = DominantPass(coefficients, (rows, cols), 3, T0)

    # Extragem lista subordonata, care contine coeficientii care au fost determinati ca fiind significant in urma pasului dominant
    subordinateList = IdentifySignificants(dominantList)

    # pastram doar valorile insignificante in dominantList, intrucat urmatorul pas dominant va parcurge doar aceste valori (insignificante)
    # dominantList contine valorile significante, care se afla si in subordonateList
    # asadar, pentru a determina valorile insignificante, facem diferenta celor doua liste
    dominantList = ListsDifference(dominantList, subordinateList)

    # efectuam pasul subordonat, in care toti coeficientii significant sunt encodati cu 0 si 1 avand in vedere pozitia in intervalul de incertitudin, Te
    subordinateList0 = SubordinatePass(subordinateList, T0, 0)

    ####################################################################################################################
    # in acest punct, in subordonateList avem valorile significante, codificate si avand noua valoare de reconstructie #
    # iar in dominantList avem acele valori care nu au fost inca descoperite ca fiind significante                     #
    # doar asupra acestor valori se va realiza mai departe pasul dominant                                              #
    ####################################################################################################################

    # determinam noul threshold ca jumatatea primului threshold
    T1 = int(T0/2)

    dominantList, coefficients = DominantPass(coefficients, (rows, cols), 3, T1)
    subordinateList = IdentifySignificants(dominantList)
    for element in subordinateList:
        subordinateList0.append(element)
    dominantList = ListsDifference(dominantList, subordinateList)
    subordinateList = SubordinatePass(subordinateList0, T0, 1)


    printList(subordinateList0)
    print("xxxxxxxxxxxxxxxxxx")
    printList(dominantList)

