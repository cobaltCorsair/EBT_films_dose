import unittest
import filters
import tifffile
import matplotlib.pyplot as plt


class MyTestCase(unittest.TestCase):
    def test_gaussianFilter(self):
        fl = r'V:\!Установки\EBT3\Без верификация фантом головы\P_bv2_150dpi127.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]

        filt1 = filters.Filter(reds)
        filt1.setFilter(filters.Filters.Gaussian_05)
        filt1.parse()
        filt2 = filters.Filter(reds)
        filt2.setFilter(filters.Filters.Gaussian_2)
        filt2.parse()

        fig, ((ax0, ax1, ax2), (ax3, ax4, ax5)) = plt.subplots(ncols=3, nrows=2)
        ax0.imshow(reds, cmap=plt.cm.jet)
        ax0.set_title("Original")
        ax1.imshow(filt1.get(), cmap=plt.cm.jet)
        ax1.set_title("Gaussian 0.5")
        ax2.imshow(filt2.get(), cmap=plt.cm.jet)
        ax2.set_title("Gaussian 2.0")
        ax3.plot(reds[100, :])
        ax3.set_ylim([0, 65535])
        ax4.plot(filt1.get()[100, :])
        ax4.set_ylim([0, 65535])
        ax5.plot(filt2.get()[100, :])
        ax5.set_ylim([0, 65535])
        #plt.imshow(reds, cmap=plt.cm.jet)
        plt.show()
        self.assertEqual(True, True)

    def test_medianFilter(self):
        fl = r'V:\!Установки\EBT3\Без верификация фантом головы\P_bv2_150dpi127.tif'
        im = tifffile.imread(fl)
        reds = im[0:im.shape[0], 0:im.shape[1], 0]

        filt1 = filters.Filter(reds)
        filt1.setFilter(filters.Filters.Median_20)
        filt1.parse()
        fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(ncols=2, nrows=2)
        ax0.imshow(reds, cmap=plt.cm.jet)
        ax0.set_title("Original")
        ax1.imshow(filt1.get(), plt.cm.jet)
        ax1.set_title("Median 20x20")
        ax2.plot(reds[100, :])
        ax3.plot(filt1.get()[100, :])
        plt.show()

    def test_something(self):
        #self.assertEqual(True, False)  # add assertion here
        pass


if __name__ == '__main__':
    unittest.main()
