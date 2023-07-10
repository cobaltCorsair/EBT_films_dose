from PyQt5.QtCore import QThread
from PyQt5 import QtCore
import numpy as np
import tifffile as tifimage
from DosesAndPaths import DosesAndPaths
from scipy.optimize import curve_fit
from GraphicsPlotting import GraphicsPlotting


application = None

class Dose(QThread):
    """
    Calculate dose
    """
    progressChanged = QtCore.pyqtSignal(int)

    def __init__(self, zero_dose, zero_dose_for_irrad_film, calibrate_list, doses_list, irradiation_film, sigma,
                 func_name):
        super().__init__()
        self.zero_dose = zero_dose
        self.zero_dose_for_irrad_film = zero_dose_for_irrad_film
        self.calibrate_list = calibrate_list
        self.irradiation_film = irradiation_film
        self.setting_doses = doses_list
        self.sigma = sigma
        self.func_name = func_name

    def run(self):
        """
        Start thread
        """
        self.red_channel_calc()
        self.calculate_calibrate_film()
        self.calc_dose_map()

    @staticmethod
    def fit_func(func_name):
        """
        Returns the static method defining the approximation function
        :param func_name: method name
        """
        functions = {
            'base fit_func': Dose.fit_func1,
            'fit_func_pol2': Dose.fit_func_pol2,
            'fit_func_pol3': Dose.fit_func_pol3,
            'fit_func_pol5': Dose.fit_func_pol5
        }
        if func_name in functions:
            return functions[func_name]

    @staticmethod
    def fit_func1(od, a, b, c):
        """
        Fitting function for calibration curve
        :param od:
        :param a:
        :param b:
        :param c:
        :return:
        """
        return (b / (od - a)) + c

    @staticmethod
    def fit_func_pol2(od, x2, x1, x0):
        '''
        Fit with x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x2, x1, x0])
        return func(od)

    @staticmethod
    def fit_func_pol3(od, x3, x2, x1, x0):
        '''
        Fit with x3*od**3+x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x3, x2, x1, x0])
        return func(od)

    @staticmethod
    def fit_func_pol5(od, x5, x4, x3, x2, x1, x0):
        '''
        Fit with x5*od**5+x4*od**4+x3*od**3+x2*od**2+x1*od+x0
        '''
        func = np.poly1d([x5, x4, x3, x2, x1, x0])
        return func(od)

    @staticmethod
    def get_imarray(img):
        im = tifimage.imread(img)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        return imarray

    def red_channel_calc(self):
        """
        Calculate value in red channel of blank field
        :return: od_blank
        """
        blank_field_path = self.zero_dose
        od_blank = np.mean(Dose.get_imarray(blank_field_path))
        print("Blank field value: ", round(od_blank, 2))

        DosesAndPaths.red_channel_blank = od_blank
        return od_blank

    def calc_dose(self, path_to_film):
        """
        Image file processor
        """
        red_channel_current_tiff = np.mean(Dose.get_imarray(path_to_film))
        od_current_dose = np.log10(DosesAndPaths.red_channel_blank / red_channel_current_tiff)

        return od_current_dose

    def find_best_fit(self, path_to_film):
        """
        Finding best fit dose and writes it to the list
        """
        od_current_dose = self.calc_dose(path_to_film) - self.zero_dose
        DosesAndPaths.calculation_doses.append(od_current_dose)

    def calculate_calibrate_film(self):
        """
        Calculating dose for each file
        """
        # сначала считаем нулевую дозу
        self.zero_dose = self.calc_dose(list(self.calibrate_list)[0])
        # затем считаем для каждого файла с использованием посчитанной нулевой
        for i in self.calibrate_list:
            self.find_best_fit(i)
        try:
            p_opt, p_cov = curve_fit(self.fit_func(self.func_name), np.array(DosesAndPaths.calculation_doses[1:]),
                                     np.array(self.setting_doses[1:]),
                                     sigma=np.array(self.setting_doses[1:]) * (self.sigma / 100))
            DosesAndPaths.p_opt = p_opt
        except (ValueError, RuntimeError):

            print('Incorrect sigma value')

    @staticmethod
    def choose_orig_or_crop():
        """
        Select the variable to be passed to the function depending on its state
        :return: DosesAndPaths.irrad_film_array or DosesAndPaths.irrad_film_array
        """
        if DosesAndPaths.irrad_film_array is not None and DosesAndPaths.irrad_film_array_original is not None:
            return DosesAndPaths.irrad_film_array
        if DosesAndPaths.irrad_film_array is None and DosesAndPaths.irrad_film_array_original is not None:
            return DosesAndPaths.irrad_film_array_original
        if DosesAndPaths.irrad_film_array is not None and DosesAndPaths.irrad_film_array_original is None:
            return DosesAndPaths.irrad_film_array

    def calc_dose_map(self):
        """
        Working with user image
        """
        try:
            zero_dose_for_irrad_film = self.calc_dose(self.zero_dose_for_irrad_film)
            print("\nShape of scanned film:", np.shape(self.choose_orig_or_crop()))
            progress = 0
            counter = 0
            print("\nPrepearing your file:\n")
            for i in np.nditer(self.choose_orig_or_crop()):
                x = np.log10(DosesAndPaths.red_channel_blank / i)
                x = x - zero_dose_for_irrad_film
                x = self.fit_func(self.func_name)(x, *DosesAndPaths.p_opt)
                DosesAndPaths.z = np.append(DosesAndPaths.z, x)

                counter = counter + 1
                if counter % 10000 == 0:
                    print("Iteration ", counter, "/", np.size(application.choose_orig_or_crop()))
                    progress += 1
                    self.progressChanged.emit(round(progress))

            DosesAndPaths.z = DosesAndPaths.z.reshape(np.shape(application.choose_orig_or_crop()))
            print("\nDose calculation ended!!!\n")
            self.progressChanged.emit(100)
            GraphicsPlotting().draw_dose_map(DosesAndPaths.z)
        except ValueError:
            print('No files found')