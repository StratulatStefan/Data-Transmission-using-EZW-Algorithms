from api.general_use import *
import time
import math

#####################################################################################
# Toate implementarile urmatoare au in vedere abordarea SAQ, prezentata in document #
#####################################################################################

# alfabetul simbolurilor disponibile pentru definirea tipului de coeficient
SymbolAlphabet = ["POS", "NEG", "IZ", "ZTR", "Z"]

# implementam descrierea unui obiect (o clasa) pentru a interpreta mai eficient detalii despre fiecare coeficient din Dominant List
class DominantListItem:
    def __init__(self, subband, coefficient):
        self.Subband(subband)
        self.Coefficient(coefficient)

    def Subband(self, subband : str):
        self.subband : str = subband

    def Coefficient(self, coeff : int):
        self.coefficient : int = coeff

    def Symbol(self, symbol : str):
        if symbol not in SymbolAlphabet:
            raise Exception("Invalid symbol!")
        self.symbol : str = symbol

    def Reconstruction(self, reconstruction : int):
        self.reconstruction = reconstruction

    def __str__(self):
        return f"Coefficient [{self.coefficient}] === Symbol [{self.symbol}] === Reconstruction [{self.reconstruction}]"

# Threshold-ul initial se alege astfel incat sa fie mai mare decat jumatatea maximului valorilor absolute ale coeficientilor
# T0 > |Xj| / 2 (unde Xj, reprezinta oricare dintre coeficienti)
# Se asemenea, conform SAQ, se prefera ca T0 sa fie putere a lui 2
# Asadar, determinam primul numar putere a lui 2, mai mare decat jumatatea valorii maxime dintre valorile absolute ale coeficientilor
def GetInitialThreshold(image):
    # valorile absolute ale coeficientilor
    abs_coefs = abs(image)

    # jumatatea valoarii maxima dintre coeficienti
    max_abs_coef = np.max(abs_coefs) / 2

    # determinam threshold-ul ca fiind cea mai apropiata valoare mai mare decat max_abs_coef, si putere a lui 2
    power = np.ceil(np.log2(max_abs_coef))
    threshold = np.power(2, power)

    return int(threshold)

# functie care analizeaza matricea de coeficienti si returneaza limitele nivelelor de descompunere in subbenzi
def GetDecompositionLimits(dimensions, decomposition_levels):
    rows, cols = dimensions

    decomposition_limits = []
    for level in range(1, decomposition_levels + 1):
        row_level = rows / np.power(2, level)
        col_level = cols / np.power(2, level)
        decomposition_limits.append((row_level, col_level))

    return decomposition_limits

# functie care descompune o imagine in subbenzile coresp. fiecarui nivel (imaginea reprezinta descompunerea pe nivele de wavelets coeficients)
    '''
    #########
    # Input #
    #########
  
    ----------------------------------------------------
    | LL3 | HL3 |            |                         |
    |-----------|    HL2     |                         |
    | LH3 | HH3 |            |                         |
    |----------------------- |           HL1           |
    |           |            |                         |
    |    LH2    |    HH2     |                         |
    |           |            |                         |
    ----------------------------------------------------
    |                        |                         |
    |                        |                         |
    |                        |                         |
    |          LH1           |           HH1           |
    |                        |                         |
    |                        |                         |
    |                        |                         |
    ----------------------------------------------------
      
    ##########
    # Output #
    ##########
    - fiecare subbanda de pe fiecare nivel in parte
  
    '''

def SubbandsDecompose(image, decomposition_levels):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # determinam limitele pentru diferite subbenzi
    decomposition_limits = GetDecompositionLimits(image.shape, decomposition_levels)

    # determinam subbenzile
    subbands = {}
    previous = decomposition_limits[0]
    for index, limits in enumerate(decomposition_limits):
        row_level, col_level = CoordinatesToInt(limits)
        prev_row_level, prev_col_level = CoordinatesToInt(previous)
        if index + 1 == decomposition_levels:
            # nu avem nevoie decat de LL de la ultimul nivel de descompunere
            subbands[f'LL{index + 1}'] = image[:row_level, :col_level]
        subbands[f'HL{index + 1}'] = image[:row_level, col_level: prev_col_level if prev_col_level != col_level else None]
        subbands[f'LH{index + 1}'] = image[row_level: prev_row_level if prev_row_level != row_level else None, : col_level]
        subbands[f'HH{index + 1}'] = image[row_level:prev_row_level if prev_row_level != row_level else None, col_level : prev_col_level if prev_col_level != col_level else None]
        previous = limits

    return subbands

# functie care reorganizeaza matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
def ReorganizeMatrix(image, decomposition_levels):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # imaginea finala va fi de forma unui vector
    final = []

    # determinam subbenzile pe nivele de descompunere coresp. matricii de coeficienti furnizata
    subbands = SubbandsDecompose(image, decomposition_levels)

    # ordinea de parcurgere : descrescatoare a nivelului
    # lista de chei care definesc tipurile de subbenzi
    subbands_keys = get_dict_keys(subbands)

    # ordine de parcurgere : LL, HL, LH, HH
    candidates = ["LL", "HL", "LH", "HH"]
    for level in range(decomposition_levels, 0, -1):
        levels = SearchStringInList(subbands_keys, f"{level}")

        for candidate in candidates:
            candi = SearchStringInList(levels, candidate)
            if len(candi) > 0:
                final.append(subbands[candi[0]])

    final = list(map(lambda el : numpyarray_to_list(el), final))

    # face lista flatten (lista de liste devine lista)
    final = ListFlatter(ListFlatter(final))
    return final

# - functie care efectueaza pasul dominant
# - analiza nu se face pe o matrice descompusa de nivel 3, ci pe componente individuale ale acestei descompuneri, pentru o parcurgere
# mai eficienta
# - atentie la nr. de decomposition_levels (modificare formule ca sa mearga cu n decomposition_levels)
def DominantPass(image, decomposition_levels, threshold):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # cream lista da valori dominante
    dominantList = []

    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # se asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    start = time.perf_counter_ns()
    coefficients = ReorganizeMatrix(image, decomposition_levels) # < 100 microsecunde
    stop = time.perf_counter_ns()

    print(f"Timp in microsecunde : {(stop - start) / 1e3}")

    initial_reconstruction_value = None
    # parcurgem lista de coeficienti si identificam tipul fiecarei valori
    for index, coefficient in enumerate(coefficients):
        # coeficientul are valoarea infinit daca se doreste ca acesta sa nu mai fie parcurs
        # cu alte cuvinte, cazul in care este descendentul unui ZeroTreeRoot
        if coefficient == np.Inf: continue

        # identificam linia si coloana pe care se afla coeficientul curent
        coef_row, coef_cols = GetRowAndColumnByIndex(index, rows, cols)

        # determinam tipul coeficientului dupa valoarea
        if abs(coefficient) > threshold:
            candidate, initial_reconstruction_value = HandleSignificantCoefficient(coefficient, initial_reconstruction_value, threshold)
        else:
            candidate = HandleInSignificantCoefficient(coefficients, index, decomposition_levels, threshold)

        # adaugam coeficientul curent in lista
        dominantList.append(candidate)

    for el in dominantList:
        print(el)
    print("#########################################")
    significants = IdentifySignificants(dominantList)
    for el in significants:
        print(el)



# functie care returneaza coeficientii significati rezultati in urma primului pas dominant
# determinarea acestora se face pe baza atributului "Symbol" din clasa ce defineste coeficientul
def IdentifySignificants(dominantList):
    significant_identifiers = ["POS", "NEG"]
    return list(filter(lambda element : element.symbol in significant_identifiers, dominantList))


# functie pentru tratarea unui coeficient significant
def HandleSignificantCoefficient(coefficient, initial_reconstruction_value, threshold):
    # avem un coeficient significant
    sign = 1 if coefficient > 0 else -1

    # initializam un nou tip de element pentru lista de coeficienti dominanti
    candidate = DominantListItem("subband not defined yet", coefficient)

    # setam tipul simbolului
    candidate.Symbol("POS" if sign == 1 else "NEG" if sign == -1 else None)

    # in acest moment se cunoaste valoarea coeficientului si tipul acestuia
    # intalnim un coeficient significant, deci trebuie sa determinam valoarea de reconstructie
    # valoare de reconstructie reprezinta jumatatea intervalului det. de threshold si coeficientul curent
    if initial_reconstruction_value == None:
        initial_reconstruction_value = int(round((abs(coefficient) + threshold) / 2))

    # valoarea de reconstructie are acelasi semn cu coeficientul
    reconstruction_value = initial_reconstruction_value * (-1 if sign == -1 else 1)
    candidate.Reconstruction(reconstruction_value)

    return candidate, initial_reconstruction_value

# functie pentru tratarea unui coeficient insignificant
def HandleInSignificantCoefficient(coefficients, index, decomposition_levels, threshold):
    coefficient = coefficients[index]

    # initializam un nou tip de element pentru lista de coeficienti dominanti
    candidate = DominantListItem("subband not defined yet", coefficient)

    # avem un coeficient insignificant

    # verificam daca acesta mai are descendenti significanti, caz in care este considerat Isolated Zero
    # daca acesta are doar descendenti insignificanti, este considerat Zero Tree Root

    # parcurgem descendentii si verificam statusul lor
    subbands = []
    current_level = decomposition_levels - int(np.floor(math.log(index, 4)))
    if current_level == 1:
        candidate = DominantListItem("subband not defined yet", coefficient)
        candidate.Reconstruction(0)
        candidate.Symbol("Z")
    elif current_level == decomposition_levels:
        for higher_level in range(1, current_level):
            inferior_limit = np.power(4, current_level - higher_level) * index
            superior_limit = np.power(4, current_level - higher_level) * (index + 1)
            subbands.append((inferior_limit, superior_limit))
    else:
        divizor = index % np.power(4, current_level) - 4
        step = int(np.power(int(4 / 2), decomposition_levels - current_level))
        inferior_limit_0 = np.power(4, current_level) + int(4/2) * (divizor) + 4 * int(divizor / 2)
        superior_limit_0 = inferior_limit_0 + step
        inferior_limit_1 = inferior_limit_0 + np.power(4, current_level - 1)
        superior_limit_1 = inferior_limit_1 + step
        subbands.append((inferior_limit_0, superior_limit_0, inferior_limit_1, superior_limit_1))

    significant_desc_found = False
    for index in range(current_level - 1):
        current_interval = subbands[index]
        inferior_limit_0 = current_interval[0]
        superior_limit_1 = current_interval[-1]
        superior_limit_0 = None
        inferior_limit_1 = None
        if len(current_interval) > 2:
            superior_limit_0 = current_interval[1]
            inferior_limit_1 = current_interval[2]
        idx = inferior_limit_0
        # vrem sa putem schimba indexul iterator ; for idx in range nu ne permite acest lucru ; asadar folosind un while
        if significant_desc_found == True:
            break
        while idx < superior_limit_1:
            if idx == superior_limit_0:
                idx += (inferior_limit_1 - superior_limit_0)
            # prelucrare valoare (verificare tip valoarea)
            if abs(coefficients[idx]) > threshold:
                # s-a gasit un descendent significant, deci elementul curent nu poate fi considerat ZeroTreeRoot
                significant_desc_found = True
                break
            idx += 1

        # initializam un nou tip de element pentru lista de coeficienti dominanti
        candidate.Reconstruction(0)
        if significant_desc_found == True:
            candidate.Symbol("IZ")
        else:
            # coeficientul curent este un ZTR intrucat nu are niciun descendent significant
            candidate.Symbol("ZTR")

            # parcurgem din nou toti descendentii si ii marcam cu inf pentru a fi ignorati la urmatoarele parcurgeri
            idx = inferior_limit_0
            while idx < superior_limit_1:
                if idx == superior_limit_0:
                    idx += (inferior_limit_1 - superior_limit_0)
                # prelucrare valoare (verificare tip valoarea)
                coefficients[idx] = np.inf
                idx += 1

    return candidate