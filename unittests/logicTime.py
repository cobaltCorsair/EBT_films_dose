import unittest
from database import dbProxy
from pymongo import MongoClient
import logicParser
from database import dbProxy
import tifffile


class MyTestCase(unittest.TestCase):
    def test_something(self):
        #self.collectionTifProvider.find_one({})
        zr1 = dbProxy.getZeroFilmData4ExactLotNo(self.collectionTifProvider, 'Co-60 (MRRC)',
                                                           '05062003', 24)
        print(zr1)
        self.assertEqual(zr1['dose'], 0.0)

    def test_build2d(self):
        fl = r'V:\!Установки\EBT3\Без верификация фантом головы\P_bv2_150dpi127.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]
        reds1d = reds.flatten()
        print(reds)
        import matplotlib.pyplot as plt
        im2 = plt.imread(fl)
        plt.imshow(reds, cmap=plt.cm.jet)
        plt.show()
        self.assertEqual(True, True)

    def test_build2d_od(self):
        fl = r'V:\!Установки\EBT3\Без верификация фантом головы\P_bv2_150dpi127.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]
        reds1d = reds.flatten()
        print(reds)

        # vl = dbProxy.getData4CalibrationCurveWithDoseHighLimit(self.collectionTifProvider, 'Co-60 (MRRC)',
        #                                                        '05062003', 24, 50.0)
        vd = dbProxy.getDict4ExactCurveWithDoseLimit(self.collectionTifProvider, 'Co-60 (MRRC)',
                                                     '05062003', 24, 50.0)

        obj1 = logicParser.LogicParser(vd, logicParser.LogicODVariant.useWhiteOD, logicParser.LogicCurveVariants.useInterp1d)
        od1d = obj1.preparePixValue(reds1d)
        print(od1d)
        import matplotlib.pyplot as plt
        #im2 = plt.imread(fl)
        plt.imshow(od1d.reshape(reds.shape), cmap=plt.cm.jet)
        plt.show()

    def setUp(self) -> None:
        self.client = MongoClient('mongodb://10.1.30.32:27017/')
        self.db = self.client['EBT_films_dose']
        self.collectionTifProvider = self.db['tifProvider']





if __name__ == '__main__':
    unittest.main()
