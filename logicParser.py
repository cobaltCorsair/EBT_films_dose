# -*- coding: utf-8 -*-
import enum
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
from scipy.interpolate import splrep, splev
import tifffile as tifimage
import sklearn
from sklearn.linear_model import Ridge
from sklearn.preprocessing import SplineTransformer
from sklearn.pipeline import make_pipeline

class LogicODVariant(enum.Enum):
    useBlackOD = 1
    useWhiteOD = 2
    # useBlackAndWhite = 3
    useDummy = 99

class LogicCurveVariants(enum.Enum):
    useCurveFit = 1
    useInterp1d = 2
    useSplev = 3
    useScikit = 4

class LogicCurveFitsVariant(enum.Enum):
    # only for useCurveFit from LogicCurveVariants
    useSerejaVariant = 1
    usePol3 = 3
    usePol4 = 4
    usePol5 = 5

def fitFuncSereja(od, a, b, c):
    return (a / (od - b)) + c

def fitFuncPol3(od, a, b, c, d):
    func = np.poly1d([a,b,c, d])
    return func(od)

def fitFuncPol4(od, a, b, c, d, e):
    func = np.poly1d([a,b,c, d, e])
    return func(od)

def fitFuncPol5(od, a, b, c, d, e, f):
    func = np.poly1d([a,b,c, d, e, f])
    return func(od)

class LogicParser(object):
    #def __init__(self, ods, doses, odVariant=LogicODVariant.useWhiteOD, curveVariant=LogicCurveVariants.useInterp1d, **kwargs):
    def __init__(self, dbDict, odVariant=LogicODVariant.useWhiteOD, curveVariant=LogicCurveVariants.useInterp1d,
                 **kwargs):
        self.__dict__['odVariant'] = odVariant
        self.__dict__['curveVariant'] = curveVariant
        if curveVariant == LogicCurveVariants.useCurveFit:
            self.__dict__['fitFunc'] = kwargs.get('fitFunc', LogicCurveFitsVariant.usePol5)


        ods = []
        doses = []
        pixzero = 0
        for item in dbDict:
            if item['isZeroFilm']:
                pixzero = item['medianRedChannel']
                continue
            od = self.preparePixValue(item['medianRedChannel'], pixzero)
            ods.append(od)
            doses.append(item['dose'])
        self.calibOds = ods
        self.calibDoses = doses
        self._prepare()

    def getPOpt(self):
        if hasattr(self, "_popt"):
            return self._popt
        else:
            return None

    @staticmethod
    def getMean4FilmByFilename(filename, channel=0):
        '''
        Функция, возвращает среднее (mean) значение по всем пикселям снимка
        @param filename: Путь к файлу
        @type filename: str
        @param channel: Канал (0 - красный, рекомендуется)
        @type channel: int
        @return:
        @rtype: float
        '''
        im = tifimage.imread(filename)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, channel])  # red channel
        mean = np.mean(imarray)
        median = np.median(imarray)
        std = np.std(imarray)
        return mean

    def _prepare(self):
        # p_opt, p_cov = curve_fit(fit_func2, x, y)
        if self.__dict__['curveVariant'] == LogicCurveVariants.useCurveFit:
            if self.__dict__['fitFunc'] == LogicCurveFitsVariant.useSerejaVariant:
                self._popt, self._pcov = curve_fit(fitFuncSereja, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol3:
                self._popt, self._pcov = curve_fit(fitFuncPol3, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol4:
                self._popt, self._pcov = curve_fit(fitFuncPol4, self.calibOds, self.calibDoses)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol5:
                self._popt, self._pcov = curve_fit(fitFuncPol5, self.calibOds, self.calibDoses)
            print(self._popt)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useInterp1d:
            self.interp = interp1d(self.calibOds, self.calibDoses)
            print(self.interp(self.calibOds))
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useSplev:
            self.splrep = splrep(self.calibOds, self.calibDoses)
            #f2a = splrep(x, y, s=0)
            #f2 = splev(np.linspace(0.0, 21.0, 1000), f2a, der=0)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useScikit:
            x = np.array(self.calibOds)
            x2 = x[:, np.newaxis]
            y = np.array(self.calibDoses)
            self.scikitmodel = make_pipeline(SplineTransformer(n_knots=4, degree=3), Ridge(alpha=1e-3))
            self.scikitmodel.fit(x2, y)
        pass

    def preparePixValue(self, PV, medUnexp=41200.0):
        if self.__dict__['odVariant'] == LogicODVariant.useBlackOD:
            medBckg = 2392.0
            #medUnexp = 41087.0 # @todo: get
            return np.log10((medUnexp - medBckg) / (PV - medBckg))
        elif self.__dict__['odVariant'] == LogicODVariant.useWhiteOD:
            medWhite = 65525.0
            #print(PV, np.log10(medWhite / PV) - np.log10(medWhite / medUnexp))
            #medUnexp = 41202.0 # @todo: get
            return np.log10(medWhite / PV) - np.log10(medWhite / medUnexp)
        elif self.__dict__['odVariant'] == LogicODVariant.useDummy:
            return np.log10(medUnexp/ PV)
        else:
            return np.log10(65535. / PV)

    def evaluate(self, value):
        od = self.preparePixValue(value)
        if self.__dict__['curveVariant'] == LogicCurveVariants.useCurveFit:
            if self.__dict__['fitFunc'] == LogicCurveFitsVariant.useSerejaVariant:
                return fitFuncSereja(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol3:
                return fitFuncPol3(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol4:
                return fitFuncPol4(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol5:
                return fitFuncPol5(od, *self._popt)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useInterp1d:
            return self.interp(od)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useSplev:
            return splev(od, self.splrep, der=0)

    def evaluateOD(self, od):
        if self.__dict__['curveVariant'] == LogicCurveVariants.useCurveFit:
            if self.__dict__['fitFunc'] == LogicCurveFitsVariant.useSerejaVariant:
                return fitFuncSereja(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol3:
                return fitFuncPol3(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol4:
                return fitFuncPol4(od, *self._popt)
            elif self.__dict__['fitFunc'] == LogicCurveFitsVariant.usePol5:
                return fitFuncPol5(od, *self._popt)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useInterp1d:
            return self.interp(od)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useSplev:
            return splev(od, self.splrep, der=0)
        elif self.__dict__['curveVariant'] == LogicCurveVariants.useScikit:
            od2 = np.array(od)
            od2 = od2[:, np.newaxis]
            return self.scikitmodel.predict(od2)
        pass

    @staticmethod
    def getNormalizedByZone(initial, x=0, y=0, w=1, h=1, cf=1.0):
        '''
        Function normalizes initial array on the new average in zone [x:x+w, y:y+h]
        @param initial: initial array
        @type initial: np.ndarray
        @param x: x corner of target slice
        @type x: int
        @param y: y corner of target slice
        @type y: int
        @param w: width of target slice
        @type w: int
        @param h: height of target slice
        @type h: int
        @param cf: target value
        @type cf: float
        @return: renozmalized array
        @rtype: np.ndarray
        '''
        sliceArr = initial[x:x+w, y:y+h]
        sliceAvg = np.average(sliceArr)
        return initial * cf / sliceAvg

if __name__ == '__main__':
    from database import dbProxy
    from pymongo import MongoClient

    client = MongoClient('mongodb://10.1.30.32:27017/')
    db = client['EBT_films_dose']
    collectionTifProvider = db['tifProvider']

    vl = dbProxy.getData4CalibrationCurveWithDoseHighLimit(collectionTifProvider, 'Co-60 (MRRC)',
                                                           '05062003', 24, 50.0)
    doses = []
    ods = []
    for dose, od in enumerate(vl):
        doses.append(dose)
        ods.append(od)

    vd = dbProxy.getDict4ExactCurveWithDoseLimit(collectionTifProvider, 'Co-60 (MRRC)',
                                                           '05062003', 24, 50.0)

    print(type(vd))
    obj1 = LogicParser(vd, LogicODVariant.useWhiteOD, LogicCurveVariants.useInterp1d)
    print(obj1.evaluateOD(0.4))
    print(obj1.evaluate(29511))

    obj2 = LogicParser(vd, LogicODVariant.useWhiteOD, LogicCurveVariants.useCurveFit, fitFunc=LogicCurveFitsVariant.useSerejaVariant)
    print(obj2.evaluateOD(0.4))
    print(obj2.evaluate(29511))

    import matplotlib.pyplot as plt
    plt.plot(np.linspace(0.01, 0.7, 100), obj1.evaluateOD(np.linspace(0.01, 0.7, 100)))
    plt.plot(np.linspace(0.01, 0.7, 100), obj2.evaluateOD(np.linspace(0.01, 0.7, 100)))
    plt.show()