import cv2 as cv
from matplotlib import pyplot

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

