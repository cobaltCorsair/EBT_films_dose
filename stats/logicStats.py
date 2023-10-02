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
    gaussWithZero = 8
    residual = 99


class universalStats(object):
    def __init__(self, obj, kind=universalFunctions.gauss, dpi=150, **kwargs):
        """
        @param obj: 2-dimensional array, where obj[0, :] treated as x and obj[1, :] treated as A
        @type obj: Union(Any, Any)
        @param kind: тип статистики
        @type kind:universalFunctions
        @param dpi: dpi изображения, если задан keyword-аргумент basisFormatter, то игнорируется
        @keyword basisFormatter: параметр скалирования оси X
        """
        self.__dict__['kind'] = kind
        #self.__dict__['dpi'] = dpi
        self.__dict__['basisFormatter'] = kwargs.get("basisFormatter", 25.4 / dpi)
        self.__dict__['isNoneObject'] = False
        if kind == universalFunctions.gauss:
            if obj[0] is None:
                x = np.arange(0, obj[1].shape[0])
                self.__dict__['isNoneObject'] = True
                y = obj[1]
            else:
                x = obj[0, :]
                y = obj[1, :]
            self.basicAssumptions = [0.5 * np.max(y), 0.5 * np.max(x), 1.0]
            self.x = x
            self.y = y
            self.__dict__['fitFunc'] = gauss
            self.__dict__['callFunc'] = prepareGaussOwnX

        elif kind == universalFunctions.polynomial:
            if obj[0] is None:
                x = np.arange(0, obj[1].shape[0])
                self.__dict__['isNoneObject'] = True
                y = obj[1]
            else:
                x = obj[0, :]
                y = obj[1, :]
            self.basicAssumptions = 3
            self.x = x
            self.y = y
            self.__dict__['fitFunc'] = np.poly1d
            self.__dict__['callFunc'] = preparePolyFit

        elif kind == universalFunctions.basic:
            if obj[0] is None:
                x = np.arange(0, obj[1].shape[0])
                self.__dict__['isNoneObject'] = True
                y = obj[1]
            else:
                x = obj[0, :]
                y = obj[1, :]
            self.basicAssumptions = 3
            self.x = x
            self.y = y

        elif kind == universalFunctions.gaussWithZero:
            if obj[0] is None:
                x = np.arange(0, obj[1].shape[0])
                self.__dict__['isNoneObject'] = True
                y = obj[1]
            else:
                x = obj[0, :]
                y = obj[1, :]
            self.basicAssumptions = [0.5 * np.max(y), 0.5 * np.max(x), 1.0, 0.0]
            self.x = x
            self.y = y
            self.__dict__['fitFunc'] = gaussWithZero
            self.__dict__['callFunc'] = prepareGaussWithZeroOwnX

        self.data = None

    def run(self):
        if self.__dict__['kind'] == universalFunctions.gauss:
            # cfs, variation = curve_fit(self.__dict__['fitFunc'], newX, x, p0=p0)
            # errs = np.sqrt(np.diag(variation))
            try:
                self.data = self.__dict__['callFunc'](self.x, self.y, self.basicAssumptions)
            except RuntimeError:
                self.data = self.basicAssumptions, [0.0, 0.0, 0.0]
        if self.__dict__['kind'] == universalFunctions.polynomial:
            try:
                self.data = self.__dict__['callFunc'](self.x, self.y, self.basicAssumptions)
                #print(type(self.data), self.data, self.data(0))
            except RuntimeError:
                self.data = np.poly1d([1, 0, 0, 0])
        if self.__dict__['kind'] == universalFunctions.gaussWithZero:
            try:
                self.data = self.__dict__['callFunc'](self.x, self.y, self.basicAssumptions)
            except RuntimeError:
                self.data = self.basicAssumptions, [0.0, 0.0, 0.0, 0.0]

    def axisHelper(self, value):
        return np.round(value / self.__dict__['basisFormatter'])

    def getMeDataForMatplotlibPlot(self):
        if self.__dict__['kind'] == universalFunctions.gauss or \
                self.__dict__['kind'] == universalFunctions.gaussWithZero:
            if self.__dict__['isNoneObject']:
                newX = np.linspace(self.x[0], self.x[-1], 10000)
                newFX = np.linspace(self.x[0], self.x[-1], 10000)
            else:
                newX = np.linspace(self.axisHelper(self.x[0]), self.axisHelper(self.x[-1]), 10000)
                newFX = np.linspace(self.x[0], self.x[-1], 10000)
            return newX, self.__dict__['fitFunc'](newFX, *self.data[0])
        elif self.__dict__['kind'] == universalFunctions.polynomial:
            if self.__dict__['isNoneObject']:
                newX = np.linspace(self.x[0], self.x[-1], 10000)
                newFX = np.linspace(self.x[0], self.x[-1], 10000)
            else:
                newX = np.linspace(self.axisHelper(self.x[0]), self.axisHelper(self.x[-1]), 10000)
                newFX = np.linspace(self.x[0], self.x[-1], 10000)
            return newX, self.data(newFX)

    def getMeDataForPrinting(self):
        if self.__dict__['kind'] == universalFunctions.gauss:
            return ([*self.data[0], 2.0*np.sqrt(2*np.log(2))*self.data[0][2]],
                    [*self.data[1], 2.0*np.sqrt(2*np.log(2))*self.data[1][2]])
        elif self.__dict__['kind'] == universalFunctions.basic:
            return vmin(self.y), vmax(self.y), mean(self.y), median(self.y)
        elif self.__dict__['kind'] == universalFunctions.polynomial:
            return self.data[0], self.data[1], self.data[2], self.data[3]
        elif self.__dict__['kind'] == universalFunctions.gaussWithZero:
            #print(self.data)
            return ([*self.data[0], 2.0*np.sqrt(2*np.log(2))*self.data[0][2]],
                    [*self.data[1], 2.0*np.sqrt(2*np.log(2))*self.data[1][2]])
            #return ([*self.data[0], 2.0*np.sqrt(2*np.log(2))*self.data[0][2]],
            #        [*self.data[1], 2.0*np.sqrt(2*np.log(2))*self.data[1][2]])


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
    return A * np.exp(-(x - mu) ** 2 / (2. * sigma ** 2))

def gaussWithZero(x, *p):
    """
    Функция, возвращает значение функции Гаусса в точке x с параметрами *p -> A (амплитуда), mu (сдвиг), sigma (сигма)
    @param x: значение x
    @type x: float
    @param p: список параметров Гаусса (амплитуда, сдвиг, сигма)
    @type p: list
    @return: вычисленное значение по распределению Гаусса
    @rtype: float
    """
    A, mu, sigma, y0 = p
    return y0 + A * np.exp(-(x - mu) ** 2 / (2. * sigma ** 2))


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

def prepareGaussWithZeroOwnX(newX, x, p0 = [1., 0., 1., 0.]):
    """
    Функция, возвращает коэффициенты [A, mu, sigma] и их ошибки, по заданному распределению массива x с адресацией
    точек массива по newX
    @param newX: значения по оси X
    @param x: значение массива в точках оси X
    @param p0: начальная подгонка, A=1., mu=0., sigma=1.
    @return:
    """
    cfs, variation = curve_fit(gaussWithZero, newX, x, p0=p0)
    errs = np.sqrt(np.diag(variation))
    return (cfs, errs,)

def polyFit(x, y, order=3):
    return np.polyfit(x, y, order)


def preparePolyFit(x, y, order=3):
    z = polyFit(x, y, order)
    return np.poly1d(z)