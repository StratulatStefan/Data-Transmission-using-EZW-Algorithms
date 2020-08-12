# acest script are ca scop evidentierea importantei folosirii unei Significance Map in cadrul transmiterii unor date printr-un canal
# de comunicatie

# sa presupunuem ca vrem sa transmitem sirul 1 2 3 0 4 0 0 0 5 6 7 0 8 9 10 0 0 1 0 123
# in loc sa trimitem tot acest sir, vom realiza un significance map care va contine 1 acolo unde avem valori semnificative
# si 0 acolo unde avem 0; astfel, vom trimite sirul 1 2 3 4 5 6 7 8 9 10 1 si significance map

# nu pare ca avem o performanta cu mult sporita insa, daca avem in vedere un mesaj in care exista legaturi intre date si putem gasi
# o modalitate eficienta de a encoda significance (ex :  ZeroTree) , performantele cresc semnificativ

import numpy
import random

def GetSignificanceMap(message):
    significance_map = list(map(lambda value : 1 if value != 0 else 0, message))
    return significance_map

def GetSignificantData(message):
    significant_data = list(filter(lambda value : value != 0, message))
    return significant_data

def DecodeData(significant_data, significance_map):
    data_aux = numpy.copy(significant_data)
    decoded = []
    # trebuie ca nr. de 1 din significance sa fie egal cu nr valorilor din significant_data
    count_ones = len(list(filter(lambda value : value == 1, significance_map)))
    if count_ones != len(significant_data):
        raise Exception("Invalid data!")
    for index in significance_map:
        if index == 1:
            decoded.append(data_aux[0])
            data_aux = data_aux[1:]
        elif index == 0:
            decoded.append(0)
        else:
            raise Exception("Invalid significance map!")
    return decoded


if __name__ == "__main__":
    # mesajul pe care dorim sa il trimitem
    message = [1, 2, 3, 0, 4, 0, 0, 5, 6, 7, 0, 8, 9, 10, 0, 0, 1, 0, 123, 12, 21, 0, 0, 0, 0, 0, 4, -1, 0, 2, 8]
    print(f"Message to send  : {message}")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    # cream significance map
    significance_map = GetSignificanceMap(message)
    print(f"Significance map : {significance_map}")

    # pastram doar datele semnificative din mesaj
    significant_data = GetSignificantData(message)
    print(f"Significant data : {significant_data}")
    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

    # recompunem sirul initial pe baza datelor semnificative si a significance map
    recomposed_data = DecodeData(significant_data, significance_map)
    print(f"Received Message : {recomposed_data}")