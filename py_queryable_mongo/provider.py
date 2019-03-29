import pymongo
from . import is_null_or_empty


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
    def database(self):
        return self._database

    def query(self, collection):
        """
        Creates a Queryable instance used to query an underlying collection
        :param collection: a MongoModel type
        :returns Queryable instance
        """
        return Queryable(self.database, collection_model)
