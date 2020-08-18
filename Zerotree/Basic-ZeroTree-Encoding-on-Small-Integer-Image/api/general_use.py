import cv2 as cv
import numpy as np
import itertools
import copy

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

# functie care sorteaza o lista de obiecte avand drept criteriu un atribut al clasei
def SortByAttribute(objects, criteria):
    return sorted(objects, key = lambda object : ClassAttributeByString(object, criteria), reverse = True)

##########################################################################################

# functie lambda care returneaza atributul unui obiect dupa nume (dat ca string)
ClassAttributeByString = lambda object, criteria : getattr(object, criteria)

##########################################################################################

# functie care realizeaza diferenta a doua liste (listA - listB)
def ListsDifference(listA, listB):
    return set(listA) - set(listB)
    # mult mai eficient decat list(filter(lambda candidate : candidate not in listB, listA))

##########################################################################################

# functie pentru afisarea la consola a unei liste de obiecte (care suprascriu functia __str__ [toString])
def printList(candidate):
    for element in candidate:
        print(element)

##########################################################################################

# functie lambda care converteste o lista de liste la un set de liste
# folosita pentru eliminarea duplicatelor dintr-o lista de liste
ListToSet = lambda lists : set(tuple(lst) for lst in lists)

##########################################################################################

# functie care primeste ca parametru o functie de obiecte si returneaza indexul primului obiect din lista al carui parametru indeplineste o conditie data
def FirstOccurence(items, criterium, values):
    for index, item in enumerate(items):
        if item != None:
            if ClassAttributeByString(item, criterium) in values:
                return index
    return -1

##########################################################################################

# functie care transforma un vector de n elemente intr-o matrice de (n/2) x (n/2) elemente
def ArrayToSquareMatrix(items):
    if len(items) == 1:
        return items
    size = int(np.sqrt(len(items)))
    result = np.zeros((size, size), np.float32)
    for i in range(size):
        for j in range(size):
            result[i, j] = items[i * size + j]
    return result

##########################################################################################

# functie care returneaza indicii de decompozitie a unei matrici de coeficienti in functie de dimensiunea imaginii si de nr. de nivele de descompunere
# se va returna o lista de liste; fiecare element (sublista din lista) va avea forma [limita_superioara_subbanda, nr._elemente_subbanda]
def GetDecompositionIndices(size, decomposition_levels):
    # extragem coordonatele dimensionale
    rows, cols = size
    if rows != cols:
        raise Exception("Rows should be equal to the Cols! Square Matrix")
    ranges = []
    for level in range(decomposition_levels):
        upper_limit = rows
        rows = int(rows/2)
        size = int(np.power(rows,2))
        ranges.append([upper_limit, size])

    ranges.reverse()
    return ranges