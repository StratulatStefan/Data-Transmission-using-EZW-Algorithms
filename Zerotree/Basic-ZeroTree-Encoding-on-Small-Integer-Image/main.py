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

    threshold = GetInitialThreshold(DWT)

    loops = 4
    subordinateList = []
    for loop in range(loops):
        # Extragem lista dominanta, care contine coeficientii care nu au fost inca determinati ca fiind significants
        dominantList, coefficients = DominantPass(coefficients, (rows, cols), 3, int(threshold / np.power(2, loop)))

        # Extragem lista subordonata, care contine coeficientii care au fost determinati ca fiind significant in urma pasului dominant
        auxiliary = IdentifySignificants(dominantList)
        for aux in auxiliary:
            subordinateList.append(aux)

        # pastram doar valorile insignificante in dominantList, intrucat urmatorul pas dominant va parcurge doar aceste valori (insignificante)
        # dominantList contine valorile significante, care se afla si in subordonateList
        # asadar, pentru a determina valorile insignificante, facem diferenta celor doua liste
        dominantList = ListsDifference(dominantList, subordinateList)

        # efectuam pasul subordonat, in care toti coeficientii significant sunt encodati cu 0 si 1 avand in vedere pozitia in intervalul de incertitudine
        subordinateList = SubordinatePass(subordinateList, threshold, loop)

        print("#############################################")
        print(f"Loop {loop + 1}")
        printList(dominantList)
        print("xxxxxx")
        printList(subordinateList)
        print("\n\n")

