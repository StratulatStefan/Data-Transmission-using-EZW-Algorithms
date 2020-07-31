from api.defined_filters import *
from api.general_use import *
from api.plotter import *

'''
-----------------------------
|      Lifting scheme       |
-----------------------------

- 50 % less computations than the convolution based-approaches
- The basic idea : use correlation in the image pixels values to remove redundancy
- Three phases : * split
                 * predict
                 * update
- Split phase : split the input sequence into two subsequences consisting of the even and odd samples.
- Predict, Update : compute high pass and low pass filtering
- More in the doc : Shahbahrami_Super_computing_Sep_2012.pdf and in the implementation

'''

# functie care realizeaza redimensionarea imaginii dupa coloane:
def RescaleByColumn(image, scale):
    x = 0

# - functie care realizeaza primul pas al Lifting-Scheme Algorithm, anume spargerea vectorului ce contine valorile imaginii
# in doi vectori, dupa paritatea indexului
# - se are in vedere paritatea dupa direction
def SplitSequence(image, direction):
    # coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # vectorul ce va contine numerele pare (dimensiune in functie de coordonatele imaginii)
    if direction == "horizontal":
        # vectorul ce va contine numerele impare
        odd = np.empty((rows, int(cols / 2)), np.float32)

        if cols % 2 == 0:
            even = np.empty(odd.shape, np.float32)
        else:
            even = np.empty((rows, int(cols/2) + 1), np.float32)

        for i in range(0, rows):
            for j in range(0, cols):
                if j % 2 == 0:
                    even[i, int(j/2)] = image[i,j]
                else:
                    odd[i, int(j/2)] = image[i, j]

    elif direction == "vertical":
        odd = np.empty((int(rows/2), cols), np.float32)

        if rows % 2 == 0:
            even = np.empty(odd.shape, np.float32)
        else:
            even = np.empty((int(rows/2) + 1, cols), np.float32)

        for i in range(0, rows):
            for j in range(0, cols):
                if i % 2 == 0:
                    even[int(i/2), j] = image[i,j]
                else:
                    odd[int(i/2), j] = image[i, j]
        print("Successfull")

    else:
        raise Exception("Invalid direction for split sequence")
    return even, odd

# functie care realizeaza a doua etapa a algoritmului Lifting-Scheme, anume Prediction Stage
# se are in vedere obtinerea valorilor high-pass
# parcurgerea vectorului se face dupa direction
def PredictionStage(splits, direction):
    # extragem cei doi vectori, cu indecsi clasificati dupa paritate
    even, odd = splits

    # formam vectorul rezultat, care va avea aceeasi dimensiune cu vectorul de indecsi impari
    hpass = np.empty(odd.shape, np.float32)

    # extragem coordonatele dimensionale
    rows, cols = odd.shape

    if direction == "horizontal":
        for i in range(0, rows, 1):
            for j in range(0, cols, 1):
                hpass[i, j] = odd[i, j] - int((even[i, j] + even[i, j + 1 if j + 1 < cols else 0]) / 2)
    elif direction == "vertical":
        for j in range(0, cols, 1):
            for i in range(0, rows, 1):
                hpass[i, j] = odd[i, j] - int((even[i, j] + even[i + 1 if i + 1 < rows else 0, j]) / 2)
        print("Successfull")

    else:
        raise Exception("Invalid direction specification for Prediction Stage!")
    return hpass

# functie care efectueaza faza a 3-a a algoritmului Lifting-Scheme
# se are in vedere obtinerea valorilor low-pass
# parcurgerea vectorului se face dupa direction
def UpdateStage(splits, direction):
    # extragem cei doi vectori, anume vectorul de indecsi pari si vectorul cu valori high pass
    high_pass, even = splits

    # formam vectorul rezultat, care va avea aceeasi dimensiune cu vectorul high pass
    lpass = np.empty(high_pass.shape, np.float32)

    # extragem coordonatele dimensionale
    rows, cols = high_pass.shape

    if direction == "horizontal":
        for i in range(0, rows, 1):
            for j in range(0, cols, 1):
                lpass[i, j] = even[i, j] + int((high_pass[i, j - 1 if j - 1 > 0 else 0] + high_pass[i, j] + 2) / 4)
    elif direction == "vertical":
        for j in range(0, cols, 1):
            for i in range(0, rows, 1):
                lpass[i, j] = even[i, j] + int((high_pass[i - 1  if i - 1 > 0 else 0, j] + high_pass[i, j] + 2) / 4)
        print("Successfull")
    else:
        raise Exception("Invalid direction specification for Update Stage!")
    return lpass

# functie care efectueaza descompunerea folosind Lifting Scheme si Daubechies-4 wavelet,
def Lifting_Scheme_Daubechies_4(image):
    # obtinem coordonatele dimensionale ale imaginii
    rows, cols = image.shape

    # cream imaginea temporara in care vom stoca valorile high pass si low rezultate din spargerea pe orizontala
    temp = np.empty(image.shape, np.float32)

    direction = "horizontal"
    even, odd = SplitSequence(image, direction)
    highpass = PredictionStage([even, odd], direction)
    lowpass = UpdateStage([highpass, even], direction)

    # compunem imaginea in formatul
    ##########################
    #            #     #     #
    #            #  L  #  H  #
    #            #     #     #
    #            #############
    temp = np.empty(image.shape, np.float32)
    temp[:,:int(cols/2)] = lowpass
    temp[:,int(cols/2):] = highpass


    direction = "vertical"
    even, odd = SplitSequence(temp, direction)
    highpass = PredictionStage([even, odd], direction)
    lowpass = UpdateStage([highpass, even], direction)
    lowpass = cv.resize(lowpass, None, fx=1.0, fy=1.0)

    # compunem imaginea finala in formatul
    ############################
    #            #  LL  #  HL  #
    #            ###############
    #            #  LH  #  HH  #
                 ###############

    temp[:int(rows/2),:] = lowpass
    temp[int(rows/2):,:] = highpass

    return temp

    # in continuare se prezinta varianta mult mai eficienta (memorie si timp) a acestui algoritm
    # nu se sparge algoritmul in pasi intermediari ce compun un pipeline, ci se executa totul dintr-o singura iteratie
    # de parcurgere a imaginii
    # FIX IT!
    '''
    # efectuam spargerea pe coloane (pe orizontala)
    # vom obtine #############
    #            #     #     #
    #            #  L  #  H  #
    #            #     #     #
    #            #############
    for i in range(0, rows, 1):
        jj = 0
        for j in range(1, cols - 1, 2):
            # calcularea valorilor high pass
            temp[i, jj + int(cols/2)] = image[i, j] - int((image[i, j - 1] + image[i, j + 1]) / 2)

            # calcularea valorilor low pass
            temp[i, j] = image[i, j - 1] + int((temp[i, jj + int(cols/2) - 1] + temp[i, jj + int(cols/2)] + 2) / 4)

            jj += 1

    # efectuam spargerea pe linii (pe verticala)
    # vom obtine ###############
    #            #  LL  #  HL  #
    #            ###############
    #            #  LH  #  HH  #
                 ###############
    result = np.empty(temp.shape, np.float32)
    jj = 0
    for j in range(1, cols - 1,2):
        jj += 1
        for i in range(0, rows, 1):
            # calcularea valorilor high-pass
            result[jj + int(cols / 2), i] = temp[j][i] - int((temp[j - 1][i] + temp[j + 1, i]) / 2)

            #calcularea valorilor low-pass
            result[jj][i] = temp[j -1][i] + int((result[jj + int(cols / 2), i] + result[jj + int(cols / 2) - 1, i] + 2) / 4)
    '''
