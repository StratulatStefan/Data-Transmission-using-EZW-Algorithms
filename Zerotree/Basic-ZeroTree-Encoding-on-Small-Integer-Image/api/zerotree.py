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
        self.Coefficient(coefficient)
        self.encoding = -1

    def Coefficient(self, coeff : int):
        self.coefficient : int = coeff

    def Symbol(self, symbol : str):
        if symbol not in SymbolAlphabet:
            raise Exception("Invalid symbol!")
        self.symbol : str = symbol

    def Reconstruction(self, reconstruction : int):
        self.reconstruction = reconstruction

    def EncodingSymbol(self, encoding : int):
        self.encoding = encoding
        '''
        if encoding == 0 or encoding == 1 or encoding == 2:
            self.encoding = encoding
        else:
            raise Exception("Invalid Encoding Value")
        '''

    def __str__(self):
        return f"Coefficient [{self.coefficient}] === Symbol [{self.symbol}] === Reconstruction [{self.reconstruction}] === Encoding [{self.encoding}]"

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
    final = [float(i) for i in final]
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
def HandleInSignificantCoefficient(coefficients, index, decomposition_levels, threshold, upper_limits):
    coefficient = coefficients[index]

    # initializam un nou tip de element pentru lista de coeficienti dominanti
    candidate = DominantListItem("subband not defined yet", coefficient)

    # avem un coeficient insignificant

    # verificam daca acesta mai are descendenti significanti, caz in care este considerat Isolated Zero
    # daca acesta are doar descendenti insignificanti, este considerat Zero Tree Root

    # parcurgem descendentii si verificam statusul lor
    subbands = []
    # tratam un caz particular al folosirii functiei logaritm (nu se poate calcula log(0))
    for limit in upper_limits:
        if index < limit:
            current_level = len(upper_limits) - upper_limits.index(limit)
            break

    cand, subbands = AnalyzeDescendents((current_level, decomposition_levels), upper_limits,coefficients, index, subbands)
    if cand != None:
        return cand

    #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#
    significant_desc_found = False

    for idx in subbands:
        if abs(coefficients[idx]) > threshold  and coefficients[idx] != -np.inf :
            significant_desc_found = True
            break

    # initializam un nou tip de element pentru lista de coeficienti dominanti
    candidate.Reconstruction(0)

    if significant_desc_found == True:
        candidate.Symbol("IZ")
    else:
        candidate.Symbol("ZTR")
        for idx in subbands:
            coefficients[idx] = np.inf

    #vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv#

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
        if iteration + 1 < iterations:
            intervals = []
            for fn in final:
                intervals.append(fn)
    return ListToSet(final)

# - functie care genereaza lista de valori care vor fi trimise
# lista valorilor de trimis se genereaza pe baza listei dominante
# lista dominanta ca contine, atat valorile insignificante, cat si cele significante, cu noua valoare de reconstructie
# - se va folosi o lista globala pentru a retine lista acestor valori care vor fi trimise, intrucat o noua iteratie de descompunere
# depinde de iteratia anterioara (de valorile ce exista deja in lista)
finalList = []
def GenerateSequenceToSend(dominant):
    finalList = []
    dominants = ["IZ", "Z", "ZTR"]
    # daca finalList este o lista goala, atunci suntem in prima iteratie de descompunere
    # in acest caz, valorile din lista dominanta vor fi adaugate in finalList
    if finalList != []:
        # suntem intr-o iteratie > 1
        # se analizeaza finalList iar valorile din lista dominanta se scriu peste valorile din finalList care au simbolul "IZ", "ZTR" sau "Z"
        # numaram cate elemente de acest tip exista in lista ("IZ", "ZTR" sau "Z")
        zeros = len(list(filter(lambda value: value.symbol in dominants, finalList)))

        # realizam o copie profunda a listei
        finalList_copy = copy.deepcopy(finalList)

        # fiecare valoare de tip Zeros este inlocuita de cate un element din dominant List
        for i in range(zeros):
            first_candidate_index = FirstOccurence(finalList_copy, "symbol", dominants)
            finalList_copy[first_candidate_index] = None
            finalList[first_candidate_index] = copy.deepcopy(dominant[0])
            dominant = dominant[1:]
    # adaugam restul elementelor din dominant List in finalList
    for el in dominant:
        finalList.append(el)

    # returnam doar datele care trebuie transmise (nu avem nevoie de tot obiectul, ci doar de atributele symbol si valoarea de reconstructie
    return list(map(lambda coefficient : [coefficient.symbol, coefficient.reconstruction], finalList))

# functie ce genereaza conventiile de encodare a significance_map
def SignificanceMapEncodingConventions():
    # lista valorilor posibile din significance_map
    # "IZ" si "Z" sunt echivalente dpv. al rezultatului final (ambele reprezinta o valoare izolata de 0)
    possible_values = ["POS", "NEG", "ZTR", "IZ"]

    # avem 4 valori deci avem nevoie doar de 2 biti (dorim sa reprezentam valorile 0, 1, 2, 3) (in loc de 24 necesari encodarii stringurilor)
    return {"IZ" : 0,"Z" : 0, "ZTR" : 1, "POS" : 2, "NEG" : 3}

# functie care codifica lista de coeficienti care va fi trimisa astfel incat sa se reduca nr de biti
# de ex, in loc sa trimitem string-ul POS (24 de biti), vor realiza o codificare in binar si vom trimite doar 3 biti
def SignificanceMapEncoding(significance_map, encoding_rules):
    # codificam significance map pe baza conventiilor
    return list(map(lambda item : encoding_rules[item], significance_map))

# - functie prin care trimitem significance_map si valorile de recontructie catre decoder
# - ar trebui sa trimitem catre celalalt RPi, dar momentam, aceasta functie doar va recompune lista de coeficienti pe baza careia se va realiza
# imaginea finala
# - aceasta functie va fi folosita la receptie
def SendEncodings(decomposition_level, size, conventions, significance_map_encoding, reconstruction_values):
    # recompunem significance_map
    # extragem toate elemente fara primul (primul este IZ, care este echivalent cu al doilea, care este Z)
    encoding_bits = list(conventions.values())[1:]
    encoding_strings = list(conventions.keys())[1:]
    significance_map = list(map(lambda item : encoding_strings[encoding_bits.index(item)],significance_map_encoding))

    # cream o lista de coeficienti de aceeasi dimensiune cu lista de coeficienti ce a fost encodata
    coefficients = [-np.inf] * (size[0] * size[1])
    index = 0
    decomposition_levels = GetDecompositionIndices(size, decomposition_level)
    subbands_upper_limits = []
    coefs_len = len(coefficients)
    for level in range(decomposition_level):
        subbands_upper_limits.append(int(coefs_len / np.power(4, decomposition_level - level - 1)))
    for signif_index, significant in enumerate(significance_map):
        #identificarea nivelului curent
        for idx, level in enumerate(decomposition_levels):
            upper_level = int(np.power(level[0], 2))
            if signif_index < upper_level:
                current_level = decomposition_level - idx
                break

        # verificam tipul elementului curent
        if significant in ["POS", "NEG"]:
            # valoarea curenta este significanta, deci extragem acest element din lista de valori si il setam in lista finala pe pozitia curenta
            if reconstruction_values != []:
                coeff = reconstruction_values[0]
            reconstruction_values = reconstruction_values[1:]
            coefficients[index] = coeff
        elif significant == "Z":
            coefficients[index] = 0
        elif significant == "ZTR":
            coefficients[index] = 0
            coarser_level_upper_level = decomposition_levels[0]
            LL_upper_limit = int(np.power(coarser_level_upper_level[0], 2) / 4)
            if signif_index < LL_upper_limit:
                # coeficientul curent se afla in LL, deci va trebui sa zerorizam toate elementele subordonate
                indexes_in_subbands = list(map(lambda idcs: idcs * coarser_level_upper_level[1] + index, [1, 2, 3]))
                if decomposition_level == 1:
                    for subband_index in indexes_in_subbands:
                        coefficients[subband_index] = 0
            else:
                indexes_in_subbands = [index]

            buffer = []
            descendents = []
            aux_cl = current_level
            for i in range(current_level - 1):
                for subband_index in indexes_in_subbands:
                    indexes = GetNextSubbands(decomposition_level, aux_cl, subbands_upper_limits, subband_index)
                    for idx in indexes:
                        buffer.append(idx)

                for el in indexes_in_subbands:
                    descendents.append(el)
                for el in buffer:
                    descendents.append(el)
                indexes_in_subbands = np.copy(buffer)
                aux_cl -= 1
            descendents = set(descendents)
            for descendent_index in descendents:
                coefficients[descendent_index] = 0
        if -np.inf in coefficients:
            index = coefficients.index(-np.inf)
    recomposed_wavelet_coefs = RecomposeDecodedCoefficients(decomposition_level, size, coefficients)
    return recomposed_wavelet_coefs

# functie folosita la receptie
# aceasta functie primeste ca input lista de coeficienti realizata in urma procesului de decodare si formeaza matricea de coeficienti
# Repara aici!
def RecomposeDecodedCoefficients(decomposition_levels, size, coefficients):
    # extragem coordonatele dimensionale pe care ar trebui sa le aiba rezultatul
    rows, cols = size
    if len(coefficients) != rows * cols:
        raise Exception("Invalid size of coefficients list!")

    # determinam nr. nivelelor de descompunere
    levels = []
    subbands_upper_limits = []
    coefs_len = len(coefficients)
    for level in range(decomposition_levels):
        subbands_upper_limits.append(int(coefs_len / np.power(4, decomposition_levels - level - 1)))

    previous_upper_level = 0
    for dec_level in range(decomposition_levels):
        upper_band_limit = subbands_upper_limits[dec_level]
        subband_size = int(upper_band_limit / 4)

        # din fiecare banda extragem cele 4 subbenzi
        for sbband_idx in range(4 if dec_level == 0 else 3):
            lower_limit = sbband_idx * subband_size + previous_upper_level
            upper_limit = (sbband_idx + 1) * subband_size + previous_upper_level
            levels.append(coefficients[lower_limit : upper_limit])
            print(f"{sbband_idx * subband_size + previous_upper_level, (sbband_idx + 1) * subband_size + previous_upper_level}")
        previous_upper_level = upper_band_limit

    subbands = ["LL", "HL", "LH", "HH"]
    final = {}
    for dec_level in range(decomposition_levels, 0, -1):
        bands = subbands[1:] if decomposition_levels != dec_level else subbands
        for subband in bands:
            coeffs = levels[0]
            levels = levels[1:]
            final[f"{subband}{dec_level}"] = coeffs

    finalMatrix = np.zeros(size, np.float32)
    prev_level = 0
    for dec_level in range(decomposition_levels, 0, -1):
        current_level = int(np.sqrt(subbands_upper_limits[decomposition_levels - dec_level]))
        current_level_half = int(current_level / 2)

        HL = ArrayToSquareMatrix(final[f"HL{dec_level}"])
        LH = ArrayToSquareMatrix(final[f"LH{dec_level}"])
        HH = ArrayToSquareMatrix(final[f"HH{dec_level}"])
        if dec_level == decomposition_levels:
            LL = ArrayToSquareMatrix(final[f"LL{dec_level}"])
            finalMatrix[prev_level:current_level_half, prev_level : current_level_half] = LL
        finalMatrix[:current_level_half, current_level_half:current_level] = HL
        finalMatrix[current_level_half : current_level, : current_level_half] = LH
        finalMatrix[current_level_half: current_level, current_level_half:current_level] = HH

        prev_level = current_level
    return finalMatrix

def AnalyzeDescendents(levels, upper_limits, coefficients, index, subbands):
    coefficient = coefficients[index]
    current_level, decomposition_levels = levels

    LL_dimension = int(upper_limits[0] / 4)
    Finnest_subband = int(upper_limits[-1] / 4)
    if index >= Finnest_subband:
        candidate = DominantListItem("subband not defined yet", coefficient)
        candidate.Reconstruction(0)
        candidate.Symbol("Z")
        return candidate, subbands

    descendents = []
    if index < LL_dimension:
        indexes_in_subbands = list(map(lambda idcs : idcs * LL_dimension + index, [1,2,3]))
        if decomposition_levels == 1:
            #subbands = list(map(lambda index : (index, index + 1), indexes_in_subbands))
            return None, indexes_in_subbands
    else:
        indexes_in_subbands = [index]

    buffer = []
    aux_cl = current_level
    for i in range(current_level - 1):
        for index in indexes_in_subbands:
            indexes = GetNextSubbands(decomposition_levels, aux_cl, upper_limits, index)
            for idx in indexes:
                buffer.append(idx)

        for el in indexes_in_subbands:
            descendents.append(el)
        for el in buffer:
            descendents.append(el)
        indexes_in_subbands = np.copy(buffer)
        aux_cl -= 1
    x = 0
    descendents = set(descendents)
    return None, descendents

def GetNextSubbands(decomposition_levels, current_level,upper_limits,index):
    subbands = []
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

    for value in range(inferior_limit_0, superior_limit_0):
        subbands.append(value)
    for value in range(inferior_limit_1, superior_limit_1):
        subbands.append(value)

    return subbands