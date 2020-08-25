from api.general_use import *

# - functie care genereaza lista de valori care vor fi trimise
# lista valorilor de trimis se genereaza pe baza listei dominante
# lista dominanta ca contine, atat valorile insignificante, cat si cele significante, cu noua valoare de reconstructie
def GenerateSequenceToSend(dominant):
    # returnam doar datele care trebuie transmise (nu avem nevoie de tot obiectul, ci doar de atributele symbol si valoarea de reconstructie
    return list(map(lambda coefficient : [coefficient.symbol, coefficient.reconstruction], dominant))


# functie ce genereaza conventiile de encodare a significance_map
def SignificanceMapEncodingConventions():
    # lista valorilor posibile din significance_map
    # "IZ" si "Z" sunt echivalente dpv. al rezultatului final (ambele reprezinta o valoare izolata de 0)
    possible_values = ["POS", "NEG", "ZTR", "IZ"]

    # avem 4 valori deci avem nevoie doar de 2 biti (dorim sa reprezentam valorile 0, 1, 2, 3) (in loc de 24 necesari encodarii stringurilor)
    return {"IZ" : 0,"Z" : 0, "ZTR" : 1, "POS" : 2, "NEG" : 3}

# functie care codifica lista de coeficienti care va fi trimisa astfel incat sa se reduca nr. de biti
# de ex, in loc sa trimitem string-ul POS (24 de biti), vor realiza o codificare in binar si vom trimite doar 3 biti
def SignificanceMapEncoding(significance_map, encoding_rules):
    # codificam significance map pe baza conventiilor
    return list(map(lambda item : encoding_rules[item], significance_map))

