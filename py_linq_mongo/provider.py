import pymongo
from .query import Queryable


class MongoProvider(object):
    __connection = None
    _database = None

    def __init__(self, mongo_client: pymongo.MongoClient, db_name: str) -> None:
        """
        Instantiates a MongoProvider from a MongoClient instance
        """
        self._connection = mongo_client
        self._database = self._connection[db_name]

    @classmethod
    def connect(
        cls,
        uri: str,
        db_name: str,
        username: str = None,
        password: str = None,
        authentication_db: str = "admin",
    ):
        """
        MongoProvider constructor
        :param uri: url of the MongoDb instance
        :param db_name: name of the MongoDb database
        :param username: if authentication is required, the username to authenticate to MongoDb with
        :param password: if authentication is required, the password to authenticate to MongoDb with
        :param authentication_db: if authentication is required, the database where username and
            password credentials are stored
        """
        cls(
            pymongo.MongoClient(
                uri,
                username=username,
                password=password,
                authSource=authentication_db,
            ),
            db_name=db_name,
        )

    @property
    def connection(self):
        return self._connection

    @property
    def database(self):
        return self._database

    def query(self, collection_type) -> Queryable:
        """
        Creates a Queryable instance used to query an underlying collection
        :param collection: a collection class
        :returns Queryable instance
        """
        if not hasattr(collection_type, "__collection_name__"):
            raise AttributeError(
                "__collection_name__ attribute not found in collection model"
            )
        if (
            collection_type.__collection_name__ is None
            or len(collection_type.__collection_name__) == 0
        ):
            raise AttributeError("__collection_name__ must be set")
        return Queryable(
            self.database[collection_type.__collection_name__], collection_type
        )
