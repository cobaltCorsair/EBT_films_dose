# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId


#client = MongoClient('mongodb://localhost:27017/')
client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collection = db['tifProvider']


