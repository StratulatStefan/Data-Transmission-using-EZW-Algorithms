from api.general_use import *
import time
import math

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


#####################################################################################
# Toate implementarile urmatoare au in vedere abordarea SAQ, prezentata in document #
#####################################################################################

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

# functie care descompune o imagine ce reprezinta descompunerea pe nivele de coeficienti Wavelet, in subbenzile coresp. fiecarui nivel
def SubbandsDecompose(image, decomposition_levels):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # determinam limitele pentru diferite subbenzi
    decomposition_limits = []
    for level in range(1, decomposition_levels + 1):
        row_level = rows / np.power(2, level)
        col_level = cols / np.power(2, level)
        decomposition_limits.append((row_level, col_level))

    # determinam subbenzile
    subbands = {}
    previous = decomposition_limits[0]
    for index, limits in enumerate(decomposition_limits):
        row_level, col_level = list(map(lambda value: int(value), limits))
        prev_row_level, prev_col_level = list(map(lambda value: int(value), previous))
        if index + 1 == decomposition_levels:
            subbands[f'LL{index + 1}'] = image[:row_level, :col_level]
        subbands[f'HL{index + 1}'] = image[:row_level,
                                     col_level: prev_col_level if prev_col_level != col_level else None]
        subbands[f'LH{index + 1}'] = image[row_level: prev_row_level if prev_row_level != row_level else None,
                                     :col_level]
        subbands[f'HH{index + 1}'] = image[row_level:prev_row_level if prev_row_level != row_level else None,
                                     col_level: prev_col_level if prev_col_level != col_level else None]
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
    subbands_keys = list(subbands.keys())

    # ordine de parcurgere : LL, HL, LH, HH
    candidates = ["LL", "HL", "LH", "HH"]
    for level in range(decomposition_levels, 0, -1):
        levels = SearchStringInList(subbands_keys, f"{level}")

        for candidate in candidates:
            candi = SearchStringInList(levels, candidate)
            if len(candi) > 0:
                final.append(subbands[candi[0]])

    final = list(map(lambda el : el.tolist(), final))

    # face lista flatten (lista de liste devine lista)
    final = ListFlatter(ListFlatter(final))
    return final

# - functie care efectueaza pasul dominant
# - analiza nu se face pe o matrice descompusa de nivel 3, ci pe componente individuale ale acestei descompuneri, pentru o parcurgere
# mai eficienta
def DominantPass(image, decomposition_levels, threshold):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # cream lista da valori dominante
    dominantList = []

    # reorganizam matricea astfel incat sa se afle in ordinea de parcurgere specifica SAQ (pe nivele)
    # se asemenea, imaginea va fi sub forma de vector pentru a fi mai usor de parcurs
    start = time.perf_counter_ns()
    coefficients = ReorganizeMatrix(image, decomposition_levels) # 65 microsecunde
    stop = time.perf_counter_ns()

    print(f"Timp in ms : {(stop - start) / 1e3}")

    initial_reconstruction_value = None
    # parcurgem lista de coeficienti si identificam tipul fiecarei valori
    for index, coefficient in enumerate(coefficients):
        print(np.Inf)
        if coefficient == np.Inf:
            continue
        # identificam linia si coloana pe care se afla coeficientul curent
        coef_row, coef_cols = GetRowAndColumnByIndex(index, rows, cols)

        # initializam un nou tip de element pentru lista de coeficienti dominanti
        candidate = DominantListItem("subband not defined yet", coefficient)

        # determinam tipul coeficientului dupa valoarea
        if abs(coefficient) > threshold:
            # avem un coeficient significant
            sign = 1 if coefficient > 0 else -1

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
        else:
            # avem un coeficient insignificant

            # verificam daca acesta mai are descendenti significanti, caz in care este considerat Isolated Zero
            # daca acesta are doar descendenti insignificanti, este considerat Zero Tree Root

            # parcurgem descendentii si verificam statusul lor
            # pentru eficienta, daca gasim unul significant, il introducem in lista pentru a nu fi iterat de mai multe ori
            subbands = []
            index = 15
            current_level = decomposition_levels - int(np.floor(math.log(index, 4)))
            if current_level == decomposition_levels:
                for higher_level in range(1,current_level):
                    # nu e buna.. mai tre putin gandit aici..
                    subbands.append((np.power(4, current_level - higher_level) * index , np.power(4, current_level - higher_level) * (index + 1)))
            else:
                divizor = index % np.power(4, current_level) - 4
                inferior_limit_0 = np.power(4, current_level) + 2 * (divizor) + 4 * int(divizor / 2)
                superior_limit_0 = inferior_limit_0 + int( np.power(4 / 2, current_level - 1))
                inferior_limit_1 = inferior_limit_0 + np.power(4, current_level - 1)
                superior_limit_1 = inferior_limit_1 + int( np.power(4 / 2, current_level - 1))
                breakpoint = True


        dominantList.append(candidate)
    breakpoint = True

