from pymongo import MongoClient


class Connect:

    @staticmethod
    def start():
        client = MongoClient('mongodb://10.1.30.32:27017/')
        db = client['EBT_films_dose']
        collectionTifProvider = db['tifProvider']

        return collectionTifProvider
