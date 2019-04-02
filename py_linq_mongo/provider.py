import pymongo
from .queryable import Queryable


class MongoProvider(object):
    __connection = None
    _database = None

    def __init__(self, uri, db_name, username=None, password=None, authentication_db=u"admin"):
        """
        MongoProvider constructor
        :param uri: url of the MongoDb instance
        :param db_name: name of the MongoDb database
        :param username: if authentication is required, the username to authenticate to MongoDb with
        :param password: if authentication is required, the password to authenticate to MongoDb with
        :param authentication_db: if authentication is required, the database where username and
            password credentials are stored
        """
        self.__connection = pymongo.MongoClient(
            uri,
            username=username,
            password=password,
            authSource=authentication_db
        )
        self._database = self.__connection[db_name]

    @property
    def connection(self):
        return self.__connection

    @property
    def database(self):
        return self._database

    def query(self, collection_type):
        """
        Creates a Queryable instance used to query an underlying collection
        :param collection: a collection class
        :returns Queryable instance
        """
        if not hasattr(collection_type, "__collection_name__"):
            raise AttributeError("__collection_name__ attribute not found in collection model")
        if collection_type.__collection_name__ is None or len(collection_type.__collection_name__) == 0:
            raise AttributeError("__collection_name__ must be set")
        return Queryable(self.database, collection_type)
