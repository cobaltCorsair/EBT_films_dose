import unittest
from stats import logicStats
import numpy as np
import logicParser
from pymongo import MongoClient
from database import dbProxy
import tifffile


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = MongoClient('mongodb://10.1.30.32:27017/')
        self.db = self.client['EBT_films_dose']
        self.collectionTifProvider = self.db['tifProvider']

    def test_something(self):
        # introducing loc variable for np.random.normal (mu variable in our notation)
        loc = 5.0
        # randomizing data
        data = np.random.normal(size=10000, loc=loc, scale=1.)
        # fitting the function and obtaining it's error
        gs, err = logicStats.prepareGauss(data)
        # checking whether obtained value of mu at gs[1] is within 3 sigma (err[1]) from original loc
        self.assertAlmostEqual(loc, gs[1], delta=3 * err[1])

    def test_funcCall(self):
        loc = 0.0
        data = np.random.normal(size=10000, loc=loc, scale=1.)
        gs, err = logicStats.prepareGauss(data)

        dte = logicStats.gauss(0.0, *gs)
        self.assertAlmostEqual(dte, gs[0], delta=3 * err[0])


    def test_polyfit1(self):
        pass
        #data = np.random.normal(size=10000, loc=0.0, scale=1.)
        #print(data)
        #hist, edges = np.histogram(data, density=True)
        #centres = (edges[:-1] + edges[1:]) / 2

        #z = logicStats.preparePolyFit(centres, hist, order=30)
        #import matplotlib.pyplot as plt
        #plt.plot(hist, data, "*")
        #plt.show()

        fl = r'V:\!Установки\EBT3\рассеяние пучка 27.05\1 all_2.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]

        reds2 = reds[690:978, 850:1138]
        print(reds.shape, reds2.shape)

        #reds1d = reds.flatten()
        #print(reds)

        # vl = dbProxy.getData4CalibrationCurveWithDoseHighLimit(self.collectionTifProvider, 'Co-60 (MRRC)',
        #                                                        '05062003', 24, 50.0)
        vd = dbProxy.getDict4ExactCurveWithDoseLimit(self.collectionTifProvider, 'Co-60 (MRRC)',
                                                     '05062003', 24, 50.0)

        obj1 = logicParser.LogicParser(vd, logicParser.LogicODVariant.useWhiteOD, logicParser.LogicCurveVariants.useSplev)
        od1d = obj1.preparePixValue(reds2)
        #print(od1d)
        dose2 = obj1.evaluateOD(od1d)
        #print(dose1d)
        import matplotlib.pyplot as plt
        #im2 = plt.imread(fl)
        fig, ax = plt.subplots(ncols=2)

        ax[0].imshow(dose2, cmap=plt.cm.jet)

        dose1slice = dose2[dose2.shape[0] // 2, :]
        ax[1].plot(dose1slice)
        p, e = logicStats.prepareGaussOwnX(np.arange(0, dose1slice.shape[0]), dose1slice)
        print(dose1slice.shape[0], "DS SHAPE")
        newX = np.linspace(0, dose1slice.shape[0], 1000)
        ax[1].plot(newX, logicStats.gauss(newX, *p))
        print(dose1slice)

        plt.show()

        pass

if __name__ == '__main__':
    unittest.main()
