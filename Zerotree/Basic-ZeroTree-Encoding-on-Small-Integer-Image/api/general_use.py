import cv2 as cv
import numpy as np
import itertools

##########################################################################################

# functie pentru tratarea unei exceptii prin afisarea unui mesaj si inchiderea programului
def BasicException(exception):
    print(f"[Exception] {exception}")
    exit(-1)

##########################################################################################

# functie lambda care returneaza o cheie dintr-un dictionar dupa index
get_dict_key_by_index = lambda dict, index : list(dict.keys())[index]

##########################################################################################

# functie lambda care returneaza o valoare dintr-un dictionar dupa index
get_dict_value_by_index = lambda dict, index : dict[get_dict_key_by_index(dict, index)]

##########################################################################################

# functie care returneaza cheile unui dictionar
get_dict_keys = lambda dictionary : list(dictionary.keys())

##########################################################################################

# functie care converteste un numpy array la o lista
numpyarray_to_list = lambda array : array.tolist()

##########################################################################################

# functie care transforma o lista de lista intr-o lista (flattering)
ListFlatter = lambda lists : list(itertools.chain(*lists))

##########################################################################################

# - functie care determina numarul ideal de procese care vor executa paralel functiile dorite
# - acest numar trebuie sa fie cat mai aproape de 10 : s-a observat experimental ca cele mai bune rezultate (timp)
# se obtin atunci cand nr. de procese este cat mai apropiat de 10
# - totodata, acest numar de procese trebuie sa fie divizor al coordonatei dimensionale pe baza careia se face divizarea (size)
def GetIdealProcessesNumber(size):
    ideal = 10

    # tratam cazul cel mai frecvent
    if size % 8 == 0:
        return 8

    # divizorii unui numar se gasesc pana la jumatatea acestuia
    half = int(size/2)

    # determinam divizorii numarului
    dividers = []
    for index in range(1, half):
        if size % index == 0:
            dividers.append(index)

    # determinam divizorul cel mai apropiat de "ideal"
    if ideal in dividers:
        return ideal

    # determinam diferenta in modul dintre fiecare divizor si 10
    candidates = list(map(lambda value : abs(value - 10), dividers))

    # indexul diferentei celei mai mici reprezinta indexul elementului cel mai apropiat de 10
    indexOfIdeal = candidates.index(min(candidates))
    ideal = dividers[indexOfIdeal]
    return ideal

##########################################################################################

# functie care transforma coordonatele dimensionale de la float la int
def CoordinatesToInt(coord):
    return list(map(lambda value : int(value), coord))

##########################################################################################

# functie care returneaza linia si coloana pe care se afla un element dintr-un vector
def GetRowAndColumnByIndex(index, rows, cols):
    row = int(index / rows)
    col = index % cols
    return row, col

##########################################################################################

# functie pentru cautarea unui template pentru un string intr-o lista
def SearchStringInList(candidates, string):
    return list(filter(lambda value : string in value, candidates))

##########################################################################################

