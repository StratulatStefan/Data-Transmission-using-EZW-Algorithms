from api.plotter import *
from api.fourier import *
from api.general_use import *

if __name__ == "__main__":
    imagePATH = "D:\Confidential\EZW Algorithm\lena.png"

    # citim imaginea
    try:
        image = ImageRead(imagePATH)
    except Exception as exc:
        print(f"[Exception] {exc}")
        exit(-1)

    mean_filter = np.ones((3, 3))

    gaussian_kernel = cv.getGaussianKernel(5, 10)
    gaussian_filter = gaussian_kernel * gaussian_kernel.T

    scharr = np.array([[-3, 0, 3],
                       [-10, 0, 10],
                       [-3, 0, 3]])
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]])
    sobel_y = np.array([[-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]])
    laplacian = np.array([[0, 1, 0],
                          [1, -4, 1],
                          [0, 1, 0]])

    filters = [mean_filter, gaussian_filter, laplacian, sobel_x, sobel_y, scharr]
    filter_names = ["mean_filter", "gaussian_filter", "laplacian", "sobel_x", "sobel_y", "scharr"]
    fourier_filters = [Fourier(filter) for filter in filters]
    spectrum = [LogScale(Magnitude(filter)) for filter in fourier_filters]

    for i in range(len(filters)):
        pyplot.subplot(f"23{i + 1}")
        pyplot.imshow(spectrum[i], cmap='gray')
        pyplot.title(filter_names[i])

    pyplot.show()