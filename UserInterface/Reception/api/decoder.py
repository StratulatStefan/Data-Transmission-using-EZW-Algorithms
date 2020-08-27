from api.general_use import *

# - functie prin care trimitem significance_map si valorile de recontructie catre decoder
# - ar trebui sa trimitem catre celalalt RPi, dar momentam, aceasta functie doar va recompune lista de coeficienti pe baza careia se va realiza
# imaginea finala
# - aceasta functie va fi folosita la receptie
def SendEncodings(decomposition_level, size, conventions, significance_map_encoding, reconstruction_values):
    # extragem toate elemente fara primul (primul este IZ, care este echivalent cu al doilea, care este Z)
    encoding_bits = list(conventions.values())[1:]
    encoding_strings = list(conventions.keys())[1:]

    # recompunem significance_map
    significance_map = list(map(lambda item : encoding_strings[encoding_bits.index(str(item))],significance_map_encoding))

    # cream o lista de coeficienti de aceeasi dimensiune cu lista de coeficienti ce a fost encodata
    # aceasta lista va contine initial doar valori infinite astfel incat sa stim unde vom adauga elementele corespunzatoare
    # nu avem nevoie de o valoarea infinita, ci doar de o valoarea care, cu siguranta, nu poate aparea.
    inf = 1 << 16
    coefficients = [inf] * (size[0] * size[1])

    index = 0
    # identificam limitele superioare ale nivelelor de descompunere (la nivel de matrice) si numarul de valorile de la fiecare nivel
    decomposition_levels = GetDecompositionIndices(size, decomposition_level)

    # identificam limitele superioare ale nivelelor de descompunere (la nivel de vector)
    subbands_upper_limits = list(map(lambda x : int(np.power(x[0], 2)), decomposition_levels))

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
            coefficients[index] = reconstruction_values[0] if reconstruction_values != [] else None
            reconstruction_values = reconstruction_values[1:]
        elif significant == "Z":
            # valoarea curenta este un Zero, deci doar aceasta valoare va fi pusa pe 0
            coefficients[index] = 0
        elif significant == "ZTR":
            # coeficientul curent este un ZeroTree, deci vom identifica toti descendentii si ii vom pune pe 0
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

            # procedeul se executa oarecum recursiv, intrucat elementele de la o iteratie depind de elementele de la iteratia anterioara
            # asadar, definim un buffer in care vom pastra elementele de la iteratia curenta pentru a putea fi folosita la iteratia urmatoare
            buffer = []

            # definim lista ce va contine descendentii finali
            descendents = []

            aux_cl = current_level
            for i in range(current_level - 1):
                for subband_index in indexes_in_subbands:
                    indexes = GetNextSubbands(decomposition_level, aux_cl, subbands_upper_limits, subband_index)

                    buffer = ListFlatter([buffer, indexes])

                descendents = ListFlatter([descendents, indexes_in_subbands, buffer])
                indexes_in_subbands = np.copy(buffer)
                aux_cl -= 1
            descendents = set(descendents)
            for descendent_index in descendents:
                coefficients[descendent_index] = 0
        for idxx in range(index, len(coefficients)):
            if coefficients[idxx] == inf:
                index = idxx
                break

    # in acest pas avem vectorul de coeficienti reconstruit
    # urmeaza sa reconstruim matricea de coeficienti pentru a putea recompune imaginea finala
    recomposed_wavelet_coefs = RecomposeDecodedCoefficients(decomposition_level, size, coefficients)

    return recomposed_wavelet_coefs

# aceasta functie primeste ca input lista de coeficienti realizata in urma procesului de decodare si formeaza matricea de coeficienti
def RecomposeDecodedCoefficients(decomposition_levels, size, coefficients):
    # extragem coordonatele dimensionale pe care ar trebui sa le aiba rezultatul
    rows, cols = size

    # avem grija ca matricea de coeficienti sa aiba aceleasi dimensiune cu vectorul de coeficienti
    if len(coefficients) != rows * cols:
        raise Exception("Invalid size of coefficients list!")

    # identificam limitele superioare ale nivelelor de descompunere (la nivel de vector)
    subbands_upper_limits = list(map(lambda level : int(len(coefficients) / np.power(4, decomposition_levels - level - 1)), range(decomposition_levels)))

    levels = []
    previous_upper_level = 0
    for dec_level in range(decomposition_levels):
        # determinam limita superioara de la banda curenta si numarul de elemente ale unei subbenzi
        upper_band_limit = subbands_upper_limits[dec_level]
        subband_size = int(upper_band_limit / 4)

        # din fiecare banda extragem cele 4 subbenzi
        # avem 4 subbenzi doar la cel mai mare nivel (coarser level) (doar aici apare LL); in rest, avem doar cele 3 (HL, LH, HH)
        for sbband_idx in range(4 if dec_level == 0 else 3):
            lower_limit = sbband_idx * subband_size + previous_upper_level
            upper_limit = (sbband_idx + 1) * subband_size + previous_upper_level
            levels.append(coefficients[lower_limit : upper_limit])
        previous_upper_level = upper_band_limit

    # compunem dictionarul cu maparea subbanda : coeficienti subbanda, pentru o recompunere mai usoara a matricii finale
    subbands = ["LL", "HL", "LH", "HH"]
    final = {}
    for dec_level in range(decomposition_levels, 0, -1):
        bands = subbands[1:] if decomposition_levels != dec_level else subbands
        for subband in bands:
            coeffs = levels[0]
            levels = levels[1:]
            final[f"{subband}{dec_level}"] = coeffs

    # definim matricea finala si plasam coeficientii la pozitiile corespunzatoare, pe baza dictionarului de subbenzi
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
