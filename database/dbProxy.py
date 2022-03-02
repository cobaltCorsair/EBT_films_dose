# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


def getListOfFacilities(collection):
    '''
    Возвращает список доступных установок облучения
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    '''
    return collection.find().distinct('facilityIdentifier')


def getListOfAvailableEBT4Facility(collection, facility=''):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    @type facility: str
    '''
    return collection.find({'facilityIdentifier': facility}).distinct('ebtLotNo')


def getListOfAvailableHoursAfterIrradiation4FacilityAndLotNo(collection, facility='', ebtLotNo=''):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    @type facility: str
    @type ebtLotNo: str
    '''
    return collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo}).distinct('hoursAfterIrrad')


def getAllLotsList(collection):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    '''
    return collection.find().distinct('ebtLotNo')


def getDict4ExactCurveWithDoseLimit(collection, facility='', ebtLotNo='', hoursAfterIrrad=24, doseLimit=0.0):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    @type facility: str
    @type ebtLotNo: str
    @type hoursAfterIrrad: int
    @type doseLimit: int
    '''
    cs = collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo, 'hoursAfterIrrad': hoursAfterIrrad,
                          'dose': {'$lt': doseLimit}}).sort('dose')
    return list(cs)

def getDict4ExactCurveWithDoseLimitWithoutZero(collection, facility='', ebtLotNo='', hoursAfterIrrad=24, doseLimit=0.0):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    @type facility: str
    @type ebtLotNo: str
    @type hoursAfterIrrad: int
    @type doseLimit: int
    '''
    cs = collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo, 'hoursAfterIrrad': hoursAfterIrrad,
                          'dose': {'$lt': doseLimit}, 'isZeroFilm': False}).sort('dose')
    return list(cs)

def getZeroFilmData4ExactLotNo(collection, facility='', ebtLotNo='', hoursAfterIrrad=24):
    '''
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    @type facility: str
    @type ebtLotNo: str
    @type hoursAfterIrrad: int
    '''
    cs = collection.find_one({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo, 'hoursAfterIrrad': hoursAfterIrrad,
                              'isZeroFilm': True})
    return cs

def storeDatabaseDirectDataSingleItem(collection, data={}):
    '''
    Функция, сохраняет одиночную запись. Не рекомендуется для прямого вызова, используйте API
    @param collection: mongodb://10.1.30.32:27017/EBT_films_dose/tifProvider
    @type collection: pymongo.collection.Collection
    '''
    collection.insert_one(data)
