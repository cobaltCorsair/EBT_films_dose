# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId
import matplotlib.pyplot as plt
import numpy as np
import os
import tifffile as tifimage


#client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']
collectionODCurves = db['ODCurves']
#collectionPOpts = db['POpts']

#collection.insert({})
postTifProvider = {
    'dose': 1.0,
    'originalTifPath': '',
    'isZeroFilm': False,
    'meanRedChannel': 50000.00,
    'medianRedChannel': 50000,
    'sigmaRedChannel': 374.22,
    'log10mean': 0.7,
    'log10meanReciprocalBlankFilm': 0.4,
    'log10meanMinusZeroFilm': 0.2,
    'ebtLotNo': '#3240017',
    'facilityIdentifier': 'Co-60',
    'hoursAfterIrrad': 24,
    'dpi': 150,
}


postODCurves = {
    'doses': [0.1, 0.7, 4.0, 20.0],
    'OD': [0.9, 0.8, 0.64, 0.32],
    'ebtLotNo': '#3240017',
    'facilityIdentifier': 'Co-60'
}

#pid = collectionODCurves.insert_one(postODCurves).inserted_id
pid = ObjectId("6179019369a8873c2afcfa42")
print(pid)

#pidCurves = collectionODCurves.find_one({"_id": pid})
#p = pidCurves['doses']
#d = pidCurves['OD']
#pdnp = np.zeros([len(p), 2])
#pdnp[:, 0] = p
#pdnp[:, 1] = d
#print(pdnp)



postPOpts = {
    'ebtLotNo': '#3240017',
    'facilityIdentifier': 'Co-60',
    'popt': [],
}

import dbProxy

print(dbProxy.getData4CalibrationCurve(collectionTifProvider, 'Co-60 (MRRC)', '01171702', 24))
print(dbProxy.getData4CalibrationCurveWithDoseHighLimit(collectionTifProvider, 'Co-60 (MRRC)', '01171702', 24, 12.0))