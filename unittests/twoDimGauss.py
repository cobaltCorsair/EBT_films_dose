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
        vd = dbProxy.getDict4ExactCurveWithDoseLimit(self.collectionTifProvider, 'Co-60 (MRRC)',
                                                     '05062003', 24, 50.0)


        fl = r'd:\dev\data\1901_octavius_20250410.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]

        reds2 = reds[457:521, 294:401]
        print(reds.shape, reds2.shape)

        obj1 = logicParser.LogicParser(vd, logicParser.LogicODVariant.useWhiteOD, logicParser.LogicCurveVariants.useSplev)
        od1d = obj1.preparePixValue(reds2)
        #print(od1d)
        dose2 = obj1.evaluateOD(od1d)
        import matplotlib.pyplot as plt
        print(dose2)
        plt.imshow(dose2, cmap=plt.cm.jet)
        #plt.show()
        x1 = np.arange(0, dose2.shape[0])
        y1 = np.arange(0, dose2.shape[1])
        xy = np.meshgrid(y1, x1)
        p, e = logicStats.prepareGauss2DFull(xy, dose2)
        print(p)
        print(e)
        print("Amplitude: %1.3f (error abs: %1.5f)" %(p[0], e[0], ))
        print("X_0: %1.3f (error abs: %1.5f)" % (p[1], e[1],))
        print("Y_0: %1.3f (error abs: %1.5f)" % (p[2], e[2],))
        print("sigma_x: %1.3f (error abs: %1.5f)" % (p[3], e[3],))
        print("sigma_y: %1.3f (error abs: %1.5f)" % (p[4], e[4],))
        print("OFFSET: %1.3f (error abs: %1.5f)" % (p[5], e[5],))
        plt.show()
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
