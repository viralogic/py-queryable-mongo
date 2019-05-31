from unittest import TestCase
import pymongo
from py_linq_mongo.query import Queryable
from . import LeagueModel, InvalidAttributeModel, EmptyCollectionNameModel


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
        query = Queryable(self.database, LeagueModel)
        count = query.count()
        self.assertEqual(1, query.count())

    def test_iterable(self):
        query = Queryable(self.database, LeagueModel)
        self.assertRaises(TypeError, query.__iter__, None)

    def test_select(self):
        query = Queryable(self.database, LeagueModel).select(lambda x: x.short_name)
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("WHL", result[0][0])

    def test_select_list(self):
        query = Queryable(self.database, LeagueModel).select(lambda x: [x.name, x.short_name])
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0][0])
        self.assertEqual("WHL", result[0][1])
