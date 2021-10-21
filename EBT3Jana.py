# Python 3.7
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os
import tifffile as tifimage
from scipy.optimize import curve_fit
import locale

#loc = locale.getlocale()
#locale.setlocale(locale.LC_ALL, ('RU', 'UTF8'))

# fitting function for calibration curve

def fit_func(od, a, b, c):
    return ((b / (od - a)) + c)


# calculate value in red chanel of blank field

#blankFieldPath = input("\nEnter path to blank field file:\n")
blankFieldPath = r'V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 05062003\24 часа после облучения\P_0MeV_150dpi_122.tif'
im = tifimage.imread(blankFieldPath)
imarray = np.array(im, dtype=np.uint16)
imarray = (imarray[:, :, 0])
odBlank = np.mean(imarray)
print("Blank field value: ", round(odBlank, 2))

# find best fit to dose-OD points

#calibrPath = input("\nPlease enter a path to folder containing calibration files:\n")
calibrPath = r'V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 12131903\48 часов после облучения'
calibrList = np.array([])

os.chdir(calibrPath)
for filename in os.listdir():

    if filename.startswith("G_"):
        im = tifimage.imread(filename)
        imarray = np.array(im, dtype=np.uint16)
        imarray = (imarray[:, :, 0])
        filename = filename[2:6].replace("p", ".")
        filename = filename.replace("_", "")
        calibrList = np.append([np.mean(imarray), filename], calibrList)

calibrList = np.reshape(calibrList, [(len(calibrList) // 2), 2])
calibrList = calibrList.astype(float)
calibrList[:, 1] = np.round(calibrList[:, 1], 2)
calibrList[:, 0] = np.log10(odBlank / calibrList[:, 0])

# тут по хоршему zeroDose нужно брать из одельного файла

zeroDose = calibrList[26, 0]
calibrList[:, 0] = calibrList[:, 0] - zeroDose
calibrList[:, 0] = np.sort(calibrList[:, 0])
calibrList[:, 1] = np.sort(calibrList[:, 1])

# тут нужен юзер инпут какую часть из всех файлов брать
calibrList = calibrList[1:15, :]

# при подборе параметров кривой юзеру должно быть предложено указать относительную погрешность (sigma)

popt, pcov = curve_fit(fit_func, calibrList[:, 0], calibrList[:, 1], sigma=calibrList[:, 1] * 0.05)
#print(calibrList[:, 0], calibrList[:, 1])
fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(calibrList[:, 0], calibrList[:, 1], ".k", markersize=6, label="Измерения")
print(popt)
ax.plot(calibrList[:, 0], fit_func(calibrList[:, 0], *popt))
# ax.set_xlim(5000,44000)
# ax.set_ylim(-1,np.amax(calibrList[;,1])+1)
ax.grid(True, linestyle="-.")
ax.set_ylabel('Поглощенная доза, Гр')
ax.set_xlabel('относительная оптическая плотность')
plt.show()

# working with user image

#userImg = input("\nPlease, enter the path to film scan you wish:\n")
userImg = r'V:\sdujenko\16.09.2021\P_1EBT_150dpi_Lot1903_233.tif'
im = tifimage.imread(userImg)
imarray = np.array(im, dtype=np.uint16)
imarray = (imarray[:, :, 0])

print("\nShape of scanned film:", np.shape(imarray))

z = []
counter = 0
print("\nPrepearing your file:\n")

for i in np.nditer(imarray):
    x = np.log10(odBlank / i)
    x = x - zeroDose
    x = fit_func(x, *popt)
    z = np.append(z, x)

    counter = counter + 1
    if counter % 10000 == 0:
        print("Iteration ", counter, "/", np.size(imarray))

z = z.reshape(np.shape(imarray))
print("\nDose calculation ended!!!\n")

fig, ax1 = plt.subplots(figsize=(9, 5))
im3 = ax1.imshow(z, cmap="jet", vmin=0, vmax=2., interpolation="gaussian")
cbar = fig.colorbar(im3, ax=ax1, orientation="vertical")
plt.show()

# \\ptcdo.proton\Shara\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 05062003\24 часа после облучения\P_0MeV_150dpi_122.tif
# \\ptcdo.proton\Shara\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 12131903\48 часов после облучения
# \\ptcdo.proton\Shara\sdujenko\16.09.2021\P_1EBT_150dpi_Lot1903_233.tif

# V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 05062003\24 часа после облучения\P_0MeV_150dpi_122.tif
# V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 12131903\48 часов после облучения
# V:\sdujenko\16.09.2021\P_1EBT_150dpi_Lot1903_233.tif