from pymongo import MongoClient
import configparser
import os

path = r'db_config.ini'


class Connect:
    """
    Connecting to the database
    """
    @staticmethod
    def start():
        parameters = Connect.read_config(path)

        client = MongoClient(parameters[0])
        db = client[parameters[1]]
        collectionTifProvider = db[parameters[2]]

        return collectionTifProvider

    @staticmethod
    def read_config(path):
        """
        Read config
        """
        if not os.path.exists(path):
            return False

        config = configparser.ConfigParser()
        config.read(path)

        ip_address = config.get("Settings", "client")
        db = config.get("Settings", "db")
        collection_tif_provider = config.get("Settings", "tifProvider")

        return [ip_address, db, collection_tif_provider]
