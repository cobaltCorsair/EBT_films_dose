# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os
import tifffile as tifimage


client = MongoClient('mongodb://localhost:27017/')
#client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
#collectionTifProvider = db['tifProvider']
collectionODCurves = db['ODCurves']
#collectionPOpts = db['POpts']

#collection.insert({})
postTifProvider = {
    'dose': 1.0,
    'originalTifPath': '',
    'isZeroFil': False,
    'meanRedChannel': 50000.00,
    'medianRedChannel': 50000,
    'sigmaRedChannel': 374.22,
    'opticalDensity': 0.7,
    'ebtLotNo': '#3240017',
    'facilityIdentifier': 'Co-60'
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

pidCurves = collectionODCurves.find_one({"_id": pid})
p = pidCurves['doses']
d = pidCurves['OD']
pdnp = np.zeros([len(p), 2])
pdnp[:, 0] = p
pdnp[:, 1] = d
print(pdnp)



postPOpts = {
    'ebtLotNo': '#3240017',
    'facilityIdentifier': 'Co-60',
    'popt': [],
}