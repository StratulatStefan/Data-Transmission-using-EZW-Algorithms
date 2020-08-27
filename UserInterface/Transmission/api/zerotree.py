from api.general_use import *

###########################################################################################
###  Toate implementarile urmatoare au in vedere abordarea SAQ, prezentata in document  ###
###########################################################################################

# implementam descrierea unui obiect (o clasa) pentru a interpreta mai eficient detalii despre fiecare coeficient din Dominant List
class DominantListItem:
    def __init__(self, coefficient):
        self.Coefficient(coefficient)
        self.encoding = -1

    def Coefficient(self, coeff : int):
        self.coefficient : int = coeff

    def Symbol(self, symbol : str):
        # alfabetul simbolurilor disponibile pentru definirea tipului de coeficient
        if symbol not in ["POS", "NEG", "IZ", "ZTR", "Z"]:
            raise Exception("Invalid symbol!")
        self.symbol : str = symbol

    def Reconstruction(self, reconstruction : int):
        self.reconstruction = reconstruction

    def EncodingSymbol(self, encoding : int):
        self.encoding = encoding

    # supraincarcam functia __str__ (toString) pentru afisarea obiectului la consola
    def __str__(self):
        return f"Coefficient [{self.coefficient}] === " \
               f"Symbol [{self.symbol}] === " \
               f"Reconstruction [{self.reconstruction}] === " \
               f"Encoding [{self.encoding}]"

# Threshold-ul initial se alege astfel incat sa fie mai mare decat jumatatea maximului valorilor absolute ale coeficientilor
# T0 > |Xj| / 2 (unde Xj, reprezinta oricare dintre coeficienti)
# Se asemenea, conform SAQ, se prefera ca T0 sa fie putere a lui 2
# Asadar, determinam primul numar putere a lui 2, mai mare decat jumatatea valorii maxime dintre valorile absolute ale coeficientilor
def GetInitialThreshold(image):
    # jumatatea valorii maxime dintre valorile absolute ale coeficientilor
    max_abs_coef = np.max(abs(image)) / 2

    # determinam threshold-ul ca fiind cea mai apropiata valoare mai mare decat max_abs_coef, si putere a lui 2
    power = np.ceil(np.log2(max_abs_coef))
    threshold = int(np.power(2, power))

    return threshold

# functie care analizeaza dimensiunile matricii de coeficienti si returneaza limitele nivelelor de descompunere
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
# functie care realizeaza descompunerea matricii de coeficienti in toate subbenzile componente de la fiecare nivel de descompunere
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
# se va returna un vector
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
            if len(candi) > 0 : final.append(subbands[candi[0]])

    final = list(map(lambda el : numpyarray_to_list(el), final))

    # face lista flatten (lista de liste devine lista)
    final = [float(i) for i in ListFlatter(ListFlatter(final))]

    return final

# - functie care efectueaza pasul dominant
# - analiza se face pe o matrice descompusa de nivel 3; se ofera ca input aceasta matrice sub forma de vector pentru o parcurgere mai eficienta
# - atentie la nr. de decomposition_levels (modificare formule ca sa mearga cu n decomposition_levels)
def DominantPass(coefficients, coordinates, decomposition_levels, threshold):
    # extragem coordonatele dimensionale ale imaginii
    rows, cols = coordinates

    # determinam limitele superioare ale subbenzilor coresp. listei de coeficienti si nivelurilor de descompunere
    subbands_upper_limits = []
    coefs_len = len(coefficients)
    for level in range(decomposition_levels):
        subbands_upper_limits.append(int(coefs_len/np.power(4, decomposition_levels - level - 1)))


    # cream lista da valori dominante
    dominantList = []

    # salvam o copie a listei de coeficienti necesara la urmatorii pasi dominanti
    # astfel, prelucrarile coeficientilor necesare la urmatorii pasi se fac pe aceasta lista
    coefficients_copy = np.copy(coefficients)

    initial_reconstruction_value = None
    # parcurgem lista de coeficienti si identificam tipul fiecarei valori
    for index, coefficient in enumerate(coefficients):
        # coeficientul are valoarea infinit daca se doreste ca acesta sa nu mai fie parcurs
        # cu alte cuvinte, cazul in care este descendentul unui ZeroTreeRoot
        if coefficient in [np.inf, -np.inf]: continue

        # identificam linia si coloana pe care se afla coeficientul curent
        coef_row, coef_cols = GetRowAndColumnByIndex(index, rows, cols)

        # determinam tipul coeficientului dupa valoarea
        if abs(coefficient) >= threshold:
            candidate, initial_reconstruction_value = HandleSignificantCoefficient(coefficient, initial_reconstruction_value, threshold)

            # setam acest coeficient cu valoarea -np.inf in lista de coeficienti astfel incat, la urmatorul pas dominant sa fie ignorati
           # coefficients_copy[index] = -np.inf
           # coefficients[index] = -np.inf
        else:
            candidate = HandleInSignificantCoefficient(coefficients, index, decomposition_levels, threshold, subbands_upper_limits)

        # adaugam coeficientul curent in lista
        dominantList.append(candidate)

    return dominantList, coefficients_copy

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
    candidate = DominantListItem(coefficient)

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
def HandleInSignificantCoefficient(coefficients, index, decomposition_levels, threshold, upper_limits):
    coefficient = coefficients[index]

    # initializam un nou tip de element pentru lista de coeficienti dominanti
    candidate = DominantListItem(coefficient)
    candidate.Reconstruction(0)

    # verificam daca acesta mai are descendenti significanti, caz in care este considerat Isolated Zero
    # daca acesta are doar descendenti insignificanti, este considerat Zero Tree Root
    # parcurgem descendentii si verificam statusul lor
    subbands = []
    for limit in upper_limits:
        if index < limit:
            current_level = len(upper_limits) - upper_limits.index(limit)
            break

    # determinam valorile indexilor descendentilor coeficientului curent
    cand, subbands = AnalyzeDescendents((current_level, decomposition_levels), upper_limits,coefficients, index, subbands)

    # functia returneaza un nou candidat in cazul in care elementul curent nu are descendenti, adica este un Zero
    # cu alte cuvinte, se afla la primul nivel de descompunere (HL1 | LH1 | HH1)
    # acest tip de element va fi returnat imediat, neavand nevoie de analiza urmatoare (a descendentilor)
    if cand != None : return cand

    # elementul curent este un ZeroTree sau un IZ; cu alte cuvinte, are descendenti
    # urmeaza sa analizam acesti descendenti si sa stabilim daca elementul este ZeroTree sau Zero Izolat
    significant_desc_found = False
    for idx in subbands:
        # verificam daca elementul este significant raportat la threshold-ul curent
        if abs(coefficients[idx]) > threshold:
            significant_desc_found = True
            break

    if significant_desc_found == True:
        # elementul are descendenti significanti, deci este un Zero Izolat
        candidate.Symbol("IZ")
    else:
        # elementul nu are descendenti significanti, deci este un ZeroTree Root
        # urmeaza sa punem toti descendentii pe inf astfel incat sa fie ignoranti in continuare, la urmatoarele iteratii
        candidate.Symbol("ZTR")
        for idx in subbands : coefficients[idx] = np.inf

    return candidate

# functie care realizeaza subordinate pass (encodarea valorilor rezultate in urma dominant pass)
# encodarea se face cu 0 si 1 avand in vedere pozitia coeficientului in intervalul de incertitudine
# de asemenea, se determina noua valoare de reconstructie pentru fiecare coeficient avand in vedere pozitia in intervalul de incertitudine
def SubordinatePass(subordonateList, threshold, iteration):
    # definim intervalul de incertitudine : [Threshold, 2 * Threshold)
    uncertaintyInterval = GetUncertaintyIntervals(iteration, threshold)

    # parcurgem lista de coeficienti significanti si codificam in raport cu decisionalValue
    for subordonate in subordonateList:
        coefficientMagnitude = abs(subordonate.coefficient)

        for index, interval in enumerate(uncertaintyInterval):
            if coefficientMagnitude >= interval[0] and coefficientMagnitude <= interval[1]:
                # valoarea decizionala va imparti intervalul de incertitudine in 2 subintervale
                # daca coeficientul se afla in primul interval (lower), va fi encodat cu 0
                # daca coeficientul se afla in al doilea interval (upper), va fi encodat cu 1
                intervalMiddle = int((interval[0] + interval[1]) / 2)

                # determinam noua valoarea de reconstructie a coeficientului, avand in vedere valoarea de encodare
                # valoarea de reconstructie se calculeaza ca media dintre valoarea decizionala si valoarea limita corespunzatoare pozitiei in interval
                if coefficientMagnitude >= intervalMiddle:
                    reconstructionMagnitude = int((intervalMiddle + interval[1]) / 2)
                    encodingValue = 1
                else:
                    reconstructionMagnitude = int((intervalMiddle + interval[0]) / 2)
                    encodingValue = 0

                # setam valoarea de encodare pentru coeficient
                subordonate.EncodingSymbol(encodingValue)
                sign = -1 if subordonate.coefficient < 0 else 1

                # setam noua valoare de reconstructie pentru coeficient
                subordonate.Reconstruction(sign * reconstructionMagnitude)

        # setam valoarea coeficientului ca fiind modulul acestuia
        #subordonate.coefficient = abs(subordonate.coefficient)

    # sortam descrescator coeficientii din lista subordonata, in functie de valoarea de reconstructie
    #subordonateList = SortByAttribute(subordonateList, "reconstruction")
    return subordonateList

# functie care returneaza intervalele de incertitudine specifice unei iteratii a procesului de identificare a tipurilor coeficientilor
def GetUncertaintyIntervals(iterations, initialThreshold):
    uncertaintyInterval = [initialThreshold, 2 * initialThreshold]
    if iterations == 0 : return ListToSet([uncertaintyInterval])
    intervals = [uncertaintyInterval]
    final = []
    for iteration in range(iterations):
        if iteration > 0 : final = []
        for interval in intervals:
            middle = int((interval[0] + interval[1]) / 2)
            final.append([interval[0], middle])
            final.append([middle, interval[1]])
        current_lower = int(initialThreshold / np.power(2, iteration + 1))
        current_upper = 2 * current_lower
        final.append([current_lower, current_upper])
        if iteration + 1 < iterations : intervals = [fn for fn in final]
    return ListToSet(final)

# functie pe care o folosim atunci cand intalnim un element insignificant si trebuie sa analizam descendentii acestuia
# in cazul identificarii descendentilor, acesta functie va returna indexul fiecarui descendent
def AnalyzeDescendents(levels, upper_limits, coefficients, index, subbands):
    coefficient = coefficients[index]
    current_level, decomposition_levels = levels

    # identificam nr. de elemente componente ale subbenzii LL
    LL_dimension = int(upper_limits[0] / 4)

    # identificam nr. de elemente componente al benzii de la primul nivel (finnest)
    Finnest_subband = int(upper_limits[-1] / 4)

    if index >= Finnest_subband:
        # daca elementul curent se afla la primul nivel, inseamna ca nu are descendenti pe care sa ii analizam
        # astfel, vom returna un candidat cu valoarea de reconstructie 0 si simbolul Z
        candidate = DominantListItem(coefficient)
        candidate.Reconstruction(0)
        candidate.Symbol("Z")
        return candidate, subbands

    # elementul curent are descendenti, pe care urmeaza sa ii identificam
    descendents = []
    if index < LL_dimension:
        # elementul curent se afla in LL si trebuie sa analizam, in primul rand, elementele din celelalte subbenzi de la acelasi nivel (HL, LH si HH)
        indexes_in_subbands = list(map(lambda idcs : idcs * LL_dimension + index, [1,2,3]))
        if decomposition_levels == 1:
            # avem un singur nivel de descompunere, iar singurii descendenti se afla la acelasi nivel in celelalte subbenzi
            return None, indexes_in_subbands
    else:
        indexes_in_subbands = [index]

    # procedeul se executa oarecum recursiv, intrucat elementele de la o iteratie depind de elementele de la iteratia anterioara
    # asadar, definim un buffer in care vom pastra elementele de la iteratia curenta pentru a putea fi folosita la iteratia urmatoare
    buffer = []
    aux_cl = current_level
    for i in range(current_level - 1):
        for index in indexes_in_subbands:
            # pentru fiecare element determinat anterior, determinam indecsii descendentilor
            indexes = GetNextSubbands(decomposition_levels, aux_cl, upper_limits, index)
            for idx in indexes:
                buffer.append(idx)

        descendents = ListFlatter([descendents, indexes_in_subbands, buffer])
        indexes_in_subbands = np.copy(buffer)
        aux_cl -= 1
    descendents = set(descendents)

    # returnam indecsii descendentilor
    return None, descendents

# functie care identifica descendentii de la urm. nivel, ai unui element
# se are in vedere ca avem corespondenta 1 : 4 (coarser : finner level)
def GetNextSubbands(decomposition_levels, current_level,upper_limits,index):
    band_size = int(upper_limits[decomposition_levels - current_level + 1] / 4)
    subband_size = int(band_size / 4)
    current_subband = int(index / subband_size)
    index_in_subband = index % subband_size
    step = int(np.sqrt(band_size)) - 2
    elements_on_the_line = int(np.sqrt(subband_size))
    current_line_in_band = int(index_in_subband / elements_on_the_line) * int(np.sqrt(band_size))
    current_line_in_subband = int(index_in_subband / elements_on_the_line) * int(np.sqrt(subband_size))
    index_in_current_line = index_in_subband % current_line_in_subband if current_line_in_subband > 0 else index_in_subband

    inferior_limit_0 = current_subband * band_size + 2 * (current_line_in_band + index_in_current_line)
    superior_limit_0 = inferior_limit_0 + 2
    inferior_limit_1 = superior_limit_0 + step
    superior_limit_1 = inferior_limit_1 + 2

    subbands = ListFlatter([range(inferior_limit_0, superior_limit_0), range(inferior_limit_1, superior_limit_1)])

    return subbands