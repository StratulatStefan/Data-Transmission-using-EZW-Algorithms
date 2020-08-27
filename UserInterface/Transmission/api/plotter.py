import cv2 as cv
from matplotlib import pyplot
import numpy as np

# libraria matplotlib pune la dispozitie clasa pyplot, prin care se pot desena imagini si grafice
# desenarea imaginilor se face in spatiul de culoare BGR; de aceea, trebuie sa convertim imaginile
# la acest spatiu de culoare inainte de a le desena
plot_calibration = lambda image : cv.cvtColor(image, cv.COLOR_GRAY2BGR)

####################################################################################################

# functie care realizeaza desenarea unei imagini intr-un grafic pyplot
# image : imaginea
# position : coordonatele subplot-ului (pozitia imaginii in fereastra de desenare)
# title : titlul subplotu-ului
def Plot(image, position, title):
    pyplot.subplot(position)
    pyplot.title(title)
    pyplot.imshow(image, cmap='gray')

# functie care ploteaza cele 4 imagini rezultate din DWT color
def PlotDWT(components, figure_index):
    pyplot.figure(num=figure_index)
    pyplot.suptitle(f"DWT Level {figure_index + 1}")

    rows, cols = list(map(lambda value : int(value/2), components.shape))
    comps = [(components[:rows, :cols], "LL"),
              (components[:rows, cols:], "HL"),
               (components[rows:, :cols], "LH"),
                (components[rows:, cols:], "HH")]
    index = 1
    # dictionarul are structura {titlu : componenta, ...}
    for coefficient in comps:
        Plot(coefficient[0], f"22{index}", coefficient[1])
        index += 1

# functie care ploteaza o descompunere DWT pe mai multe niveluri
def PlotMultiDWT(components, figure_index):
    fig_index = np.copy(figure_index)
    for component in components.values():
        PlotDWT(component, fig_index)
        fig_index += 1

# functie care creeaza o imagine care sa contina toate cele 4 subdomenii rezultate din DWT
def DWTResultComposer(items):
    # extragem cele 4 subdomenii
    LL, LH, HL, HH = items.values()

    # cream o imagine care sa aiba dimensiune dubla fata de dimensiunea unei subimagini
    # extragem cele doua dimensiuni si le dublam
    new_rows, new_cols = map(lambda size : size * 2, LL.shape)

    # cream noua imagine
    new_image = np.empty((new_rows, new_cols), np.float32)

    # redimensionam cele 4 imagini la jumatate
    LL_resized, LH_resized, HL_resized, HH_resized = map(lambda el : cv.resize(el,None, fx=1.0, fy=1.0), (LL, LH, HL, HH))

    # compunem cele 4 imagini redimensionate in noua imagine astfel
    #########################
    #   LL     #    HL      #
    #########################
    #   LH     #    HH      #
    #########################
    element_size = LL_resized.shape
    new_image[:element_size[0], :element_size[1]] = LL_resized
    new_image[:element_size[0], element_size[1]:] = HL_resized
    new_image[element_size[0]:, :element_size[1]] = LH_resized
    new_image[element_size[0]:, element_size[1]:] = HH_resized
    return new_image