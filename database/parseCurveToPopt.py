# -*- coding: utf-8 -*-

from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
from scipy.optimize import curve_fit

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

s = collectionTifProvider.find(tg).sort('dose')
for i in s:
    print(i)
