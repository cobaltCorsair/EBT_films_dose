# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from scipy.optimize import curve_fit
import dbProxy as dbProxy
from scipy.interpolate import interp1d
from scipy.interpolate import splrep, splev
import matplotlib.pyplot as plt

client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']

tg = {'ebtLotNo': '05062003', 'hoursAfterIrrad': 24, 'facilityIdentifier': 'Co-60 (MRRC)', 'dose': {'$lt': 25.0}}


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

def fit_func2(od, a, b, c, d, e):
    func = np.poly1d([a,b,c, d, e])
    return func(od)

x = []
y = []
s = collectionTifProvider.find(tg).sort('dose')
for i in s:
    print(i)
    x.append(i['dose'])
    y.append(i['log10meanMinusZeroFilm'])

p_opt, p_cov = curve_fit(fit_func2, x, y)

f1 = interp1d(x, y)

f2a = splrep(x, y, s=0)
f2 = splev(np.linspace(0.0, 21.0, 1000), f2a, der=0)

plt.plot(x, y, "*")
plt.plot(np.linspace(0.0, 25.0, 1000), fit_func2(np.linspace(0.0, 25.0, 1000), *p_opt))

plt.plot(np.linspace(0.0, 21.0, 1000), f1(np.linspace(0.0, 21.0, 1000)))
plt.plot(np.linspace(0.0, 21.0, 1000), f2)


plt.show()

print(dbProxy.getZeroFilmData4ExactLotNo(collectionTifProvider, 'Co-60 (MRRC)', '05062003', 24))