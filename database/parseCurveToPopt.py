# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']

tg = {'ebtLotNo': '05062003', 'hoursAfterIrrad': 24, 'facilityIdentifier': 'Co-60 (MRRC)', 'dose': {'$lt': 25.0, '$gt': 0.0}}


def fit_func(od, a, b, c):
    """
    Fitting function for calibration curve
    :param od:
    :param a:
    :param b:
    :param c:
    :return:
    """
    return (b / (od - a)) + c

s = collectionTifProvider.find(tg).sort('dose')
doses = []
ods = []
for i in s:
    print(i)
    doses.append(i['dose'])
    ods.append(i['log10meanMinusZeroFilm'])

print(doses, ods)
popt, pcov = curve_fit(fit_func, np.array(ods), np.array(doses), sigma=np.array(doses) * 0.03)
print(popt, np.diag(np.sqrt(pcov)))

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(ods, doses, ".k", markersize=6, label="Измерения")
print(popt)
#ax.plot(ods, fit_func(doses, *popt))

#ax.plot(np.linspace(0.0001, 0.6, 100), fit_func(np.linspace(0.0001, 0.6, 100), 0.82184782, -4.68050656, -5.75922209))

ax.plot(np.linspace(0.0001, 0.6, 100), fit_func(np.linspace(0.0001, 0.6, 100), *popt))

plt.show()
