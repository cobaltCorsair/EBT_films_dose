# -*- coding: utf-8 -*-
'''PLEASE DO NOT RUN THIS FILE DIRECTLY UNLESS IT IS INTENDED USE'''

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import numpy as np
import tifffile as tifimage
import os
from dbProxy import storeDatabaseDirectDataSingleItem as stp

def analyzeSingleFilm(fName=''):
    '''
    Возвращает словарь с ключами значений статистики плёнки по пути fName по разным каналам
    @param fName: путь к файлу для анализа
    @type fName: str
    @return:
    @rtype: dict
    '''
    if fName == '':
        return
    im = tifimage.imread(fName)
    imarray = np.array(im, dtype=np.uint16)
    imarrayRed = (imarray[:, :, 0])
    imarrayGreen = (imarray[:, :, 1])
    imarrayBlue = (imarray[:, :, 2])
    ret = {
        'log10mean': np.log10(np.mean(imarrayRed)),
        'meanRedChannel': np.mean(imarrayRed),
        'medianRedChannel': np.median(imarrayRed),
        'stdRedChannel': np.std(imarrayRed),
        'log10meanRedChannel': np.log10(np.mean(imarrayRed)),
        'meanGreenChannel': np.mean(imarrayGreen),
        'medianGreenChannel': np.median(imarrayGreen),
        'stdGreenChannel': np.std(imarrayGreen),
        'log10meanGreenChannel': np.log10(np.mean(imarrayGreen)),
        'meanBlueChannel': np.mean(imarrayBlue),
        'medianBlueChannel': np.median(imarrayBlue),
        'stdBlueChannel': np.std(imarrayBlue),
        'log10meanBlueChannel': np.log10(np.mean(imarrayBlue)),
    }
    return ret

def path2dose(fl):
    """
    Возвращает дозу из имени файла, в формате G_[целая_часть_дозы]p[дробная_часть_дозы]_[dpi]dpi.tif
    @param fl: имя файла
    @type fl: str
    @return: доза
    @rtype: float
    """
    if "G_" in fl and ".tif" in fl:
        flSpl = fl.split("_")
        dose = flSpl[1]
        dose = dose.replace("p", ".")
        dose = float(dose)
        return dose
    return -1.0

def retBaseDict(facility, ebtLotNo, hoursAfterIrrad, dpi):
    """
    Возвращает словарб с ключами, соответствующими заданным параметрам
    @param facility: идентификатор установки
    @param ebtLotNo: номер лота
    @param hoursAfterIrrad: время после облучения
    @type hoursAfterIrrad: int
    @param dpi: DPI
    @type dpi: int
    @return:
    @rtype: dict
    """
    return {
        'ebtLotNo': ebtLotNo,
        'facilityIdentifier': facility,
        'hoursAfterIrrad': hoursAfterIrrad,
        'dpi': dpi,
    }

def parseFolder2DataDict(fDir, rBase):
    '''
    Возвращает итератором словарь для вставки в базу
    Пример использовния:
    for dd in parseFolder2DataDict(fDir, rBase):
        stp(collectionTifProvider, dd)
    @param fDir: директория
    @param rBase: словарь с базовыми параметрами
    @return: генератор yield
    '''
    #fDir = r"V:\!Установки\EBT3\Калибровка Co-60\EBT3_Lot#10241901_scanner115"
    for fl in os.listdir(fDir):
        dDict = rBase.copy()
        dose = path2dose(fl)
        dDict['dose'] = dose
        if dose == 0.0:
            dDict['isZeroFilm'] = True
        else:
            dDict['isZeroFilm'] = False
        tDict = analyzeSingleFilm(os.path.join(fDir, fl))
        dDict.update(tDict)
        dDict['originalTifPath'] = os.path.join(fDir, fl)
        yield dDict

if __name__ == '__main__':
    fDir = r"V:\!Установки\EBT3\Калибровка Co-60\EBT3_Lot#10241901_scanner115_lp"
    rBase = retBaseDict('Co-60 (MRRC) sc. 115', '10241901 (rp)', 24, 150)

    client = MongoClient('mongodb://10.1.30.32:27017/')
    db = client['EBT_films_dose']
    collectionTifProvider = db['tifProvider']

    for dd in parseFolder2DataDict(fDir, rBase):
        print(dd)
        #stp(collectionTifProvider, dd)