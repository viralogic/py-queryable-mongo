from unittest import TestCase
import pymongo
from py_linq_mongo.queryable import Queryable


class LeagueModel(object):
    __collection_name__ = "team"


class InvalidAttributeModel(object):
    __invalid_name__ = "team"


class EmptyCollectionNameModel(object):
    __collection_name__ = None


class QueryableTests(TestCase):
    """
    Unit tests for Queryable class
    """
    def setUp(self):
        """
        Sets up query to collection
        """
        self.client = pymongo.MongoClient(
            host="localhost:27017",
            username="whl_user",
            password="Dawn381!",
            authSource="whl-data"
        )
        self.database = self.client["whl-data"]

    def test_constructor(self):
        query = Queryable(self.database, LeagueModel)
        self.assertIsInstance(query, Queryable)
        self.assertIsInstance(query.expression, pymongo.collection.Collection)

        self.assertRaises(AttributeError, Queryable, self.database, InvalidAttributeModel)
        self.assertRaises(AttributeError, Queryable, self.database, EmptyCollectionNameModel)

    def test_count(self):
        query = Queryable(self.collection)
        count = query.count()
        self.assertEqual(1, query.count())
