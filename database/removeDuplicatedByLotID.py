import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb://10.1.30.32:27017/')
db = client['EBT_films_dose']
collectionTifProvider = db['tifProvider']

fullColl = collectionTifProvider.aggregate([ {'$match': {'ebtLotNo': '01171702'}}])
#print(list(fullColl))

listDoses = []
listIds = []

for i in fullColl:
    #print(i)
    print(i['dose'])
    if i['dose'] not in listDoses:
        listDoses.append(i['dose'])
    else:
        listIds.append(i['_id'])

#print(listIds)
#for i in listIds:
#    collectionTifProvider.remove({'_id': i})