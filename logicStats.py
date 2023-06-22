import numpy as np
from scipy.optimize import curve_fit

def gauss(x, *p):
    """
    Функция, возвращает значение функции Гаусса в точке x с параметрами *p -> A (амплитуда), mu (сдвиг), sigma (сигма)
    @param x: значение x
    @type x: float
    @param p: список параметров Гаусса (амплитуда, сдвиг, сигма)
    @type p: list
    @return: вычисленное значение по распределению Гаусса
    @rtype: float
    """
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


def mean(x):
    """
    Вычисляет среднее значение переданного массива
    @param x: массив
    @return: среднее значение
    """
    return np.mean(x)


def median(x):
    return np.median(x)


def vmax(x):
    return np.max(x)


def vmin(x):
    return np.min(x)


def prepareGauss(x, p0 = [1., 0., 1.]):
    """
    Функция, возвращает коэффициенты [A, mu, sigma] и их ошибки, по заданному распределению массива x
    @param x:
    @param p0:
    @return:
    """
    hist, edges = np.histogram(x, density=True)
    centres = (edges[:-1] + edges[1:]) / 2

    cfs, variation = curve_fit(gauss, centres, hist, p0=p0)
    errs = np.sqrt(np.diag(variation))

    #hist_fit = gauss(centres, *cfs)

    return (cfs, errs, )


def prepareGaussOwnX(newX, x, p0 = [1., 0., 1.]):
    """
    Функция, возвращает коэффициенты [A, mu, sigma] и их ошибки, по заданному распределению массива x с адресацией
    точек массива по newX
    @param newX: значения по оси X
    @param x: значение массива в точках оси X
    @param p0: начальная подгонка, A=1., mu=0., sigma=1.
    @return:
    """
    cfs, variation = curve_fit(gauss, newX, x, p0=p0)
    errs = np.sqrt(np.diag(variation))
    return (cfs, errs,)


def polyFit(x, y, order=3):
    return np.polyfit(x, y, order)


def preparePolyFit(x, y, order=3):
    z = polyFit(x, y, order)
    return np.poly1d(z)