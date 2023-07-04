import numpy as np
from scipy.optimize import curve_fit
import enum


class universalFunctions(enum.Enum):
    basic = 0
    gauss = 1
    polynomial = 2
    landaun = 3
    guess = 4
    neural = 5
    torch = 6
    pycuda = 7
    residual = 99


class universalStats(object):
    def __init__(self, obj, kind=universalFunctions.gauss, dpi=150, **kwargs):
        self.__dict__['kind'] = kind
        #self.__dict__['dpi'] = dpi
        self.__dict__['basisFormatter'] = kwargs.get("basisFormatter", 25.4 / dpi)
        if kind == universalFunctions.gauss:
            x = obj[0, :]
            y = obj[1, :]
            self.basicAssumptions = [0.5 * np.max(y), 0.5 * np.max(x), 1.0]
            self.x = x
            self.y = y
            self.__dict__['fitFunc'] = gauss
            self.__dict__['callFunc'] = prepareGaussOwnX

        elif kind == universalFunctions.polynomial:
            x = obj[0, :]
            y = obj[1, :]
            self.basicAssumptions = 3
            self.x = x
            self.y = y
            self.__dict__['fitFunc'] = polyFit
            self.__dict__['callFunc'] = preparePolyFit

    
    def run(self):
        if self.__dict__['kind'] == universalFunctions.gauss:
            #cfs, variation = curve_fit(self.__dict__['fitFunc'], newX, x, p0=p0)
            #errs = np.sqrt(np.diag(variation))

            self.data = self.__dict__['callFunc'](self.x, self.y, self.basicAssumptions)

    def axisHelper(self, value):
        return np.round(value / self.__dict__['basisFormatter'])

    def getMeDataForMatplotlibPlot(self):
        if self.__dict__['kind'] == universalFunctions.gauss:
            newX = np.linspace(self.axisHelper(self.x[0]), self.axisHelper(self.x[-1]), 10000)
            newFX = np.linspace(self.x[0], self.x[-1], 10000)
            return newX, self.__dict__['fitFunc'](newFX, *self.data[0])
        
    def getMeDataForPrinting(self):
        if self.__dict__['kind'] == universalFunctions.gauss:
            return self.data[0], self.data[1]



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