# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import tifffile as tifimage
import os

import matplotlib.pyplot as plt

parseDir = u'V:\\!Установки\\EBT3\\Калибровка от 05.09.2021 Со-60\\Lot 05062003\\24 часа после облучения\\'
zeroFieldPath = r'V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 05062003\24 часа после облучения\G_0p0_150dpi_Lot2003.tif'

def getCharacteristrics(tifFile):
    im = tifimage.imread(tifFile)
    imarray = np.array(im, dtype=np.uint16)
    imarray = (imarray[:, :, 0]) # red channel
    mean = np.mean(imarray)
    median = np.median(imarray)
    std = np.std(imarray)
    ret = {
        'meanRedChannel': mean,
        'medianRedChannel': median,
        'stdRedChannel': std,
        'log10mean': np.log10(mean),
        'log10ReciprocalMean': np.log10(1./mean),
    }
    return ret

def getDataForDBPost(newDict, dose, infoDict, filePath='', isZero=False, zeroMean=0.0, blankMean=65526.0):
    '''
    @param newDict:
    '''
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
    ret = postTifProvider.copy()
    ret['dose'] = dose
    ret.update(newDict)
    ret.update(infoDict)
    ret['log10meanReciprocalBlankFilm'] = np.log10(blankMean / newDict['meanRedChannel'])
    if not isZero:
        ret['log10meanMinusZeroFilm'] = ret['log10meanReciprocalBlankFilm'] - np.log10(blankMean / zeroMean)
    else:
        ret['log10meanMinusZeroFilm'] = 0.0
    ret['isZeroFilm'] = isZero
    ret['originalTifPath'] = filePath
    return ret

blankFieldPath = r'V:\!Установки\EBT3\Калибровка от 05.09.2021 Со-60\Lot 05062003\24 часа после облучения\P_0MeV_150dpi_122.tif'
blankFieldData = getCharacteristrics(blankFieldPath)
print(getCharacteristrics(blankFieldPath))


zeroFieldData = getCharacteristrics(zeroFieldPath)
print(zeroFieldData)

infoDict = {
    'ebtLotNo': '05062003',
    'hoursAfterIrrad': 24,
    'facilityIdentifier': 'Co-60 (MRRC)',
    'dpi': 150,
}

#client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']

doses = []
netODs = []


for fl in os.listdir(parseDir):
    #print(fl)
    if "G_" in fl and ".tif" in fl:
        flSpl = fl.split("_")
        print(flSpl)
        dose = flSpl[1]
        dose = dose.replace("p", ".")
        dose = float(dose)
        tifData = getCharacteristrics(os.path.join(parseDir, fl))
        if dose == 0.0:
            post = getDataForDBPost(tifData, dose, infoDict, os.path.join(parseDir, fl), True, 0, float(blankFieldData['meanRedChannel']))
        else:
            post = getDataForDBPost(tifData, dose, infoDict, os.path.join(parseDir, fl), False, float(zeroFieldData['meanRedChannel']), float(blankFieldData['meanRedChannel']))
        print(post)
        #collectionTifProvider.insert_one(post)
        #doses.append(dose)
        #netODs.append(post['log10meanReciprocalBlankFilm'] - np.log10(blankFieldData['meanRedChannel'] / zeroFieldData['meanRedChannel']))


#fig, ax = plt.subplots(figsize=(9, 5))
#ax.plot(doses, netODs, ".k", markersize=6, label="Измерения")

#plt.show()

l = collectionTifProvider.find({'ebtLotNo': '05062003'})
for i in l:
    print(i)

l2 = collectionTifProvider.distinct('ebtLotNo')
print(l2)

l3 = collectionTifProvider.aggregate([{"$group": {"_id": "$ebtLotNo"}}])
print(l3)
for i in l3:
    print(i)
