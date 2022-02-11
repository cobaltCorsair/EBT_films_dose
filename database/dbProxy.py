# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId


def getListOfFacilities(collection):
    '''
    @type collection: pymongo.collection.Collection
    '''
    return collection.find().distinct('facilityIdentifier')


def getListOfAvailableEBT4Facility(collection, facility=''):
    '''
    @type collection: pymongo.collection.Collection
    '''
    return collection.find({'facilityIdentifier': facility}).distinct('ebtLotNo')


def getListOfAvailableHoursAfterIrradiation4FacilityAndLotNo(collection, facility='', ebtLotNo=''):
    '''
    @type collection: pymongo.collection.Collection
    '''
    return collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo}).distinct('hoursAfterIrrad')


def getAllLotsList(collection):
    '''
    @type collection: pymongo.collection.Collection
    '''
    return collection.find().distinct('ebtLotNo')


def getData4CalibrationCurve(collection, facility='', ebtLotNo='', hoursAfterIrrad=''):
    '''
    @type collection: pymongo.collection.Collection
    '''
    cs = collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo, 'hoursAfterIrrad': hoursAfterIrrad,
                          'dose': {'$gt': 0}}).sort('dose')
    ret = {}
    for i in cs:
        ret[i['dose']] = i['log10meanMinusZeroFilm']
    return ret


def getData4CalibrationCurveWithDoseHighLimit(collection, facility='', ebtLotNo='', hoursAfterIrrad='', doseLimit=0.0):
    '''
    @type collection: pymongo.collection.Collection
    '''
    cs = collection.find({'facilityIdentifier': facility, 'ebtLotNo': ebtLotNo, 'hoursAfterIrrad': hoursAfterIrrad,
                          'dose': {'$gt': 0.0, '$lt': doseLimit}}).sort('dose')
    ret = {}
    for i in cs:
        ret[i['dose']] = i['log10meanMinusZeroFilm']
    return ret
