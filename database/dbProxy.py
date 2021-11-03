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