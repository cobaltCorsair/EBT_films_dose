import unittest
from pymongo import MongoClient
from bson.objectid import ObjectId

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here

    def test_dummyObjectIdGetter(self):
        obj = self.collectionTifProvider.find_one({'_id': ObjectId('6182463f0813928d88e5b188')})
        self.assertEqual(obj['dose'], 35.0)

    def setUp(self):
        self.client = MongoClient('mongodb://10.1.30.32:27017/')
        self.db = self.client['EBT_films_dose']
        self.collectionTifProvider = self.db['tifProvider']


if __name__ == '__main__':
    unittest.main()
