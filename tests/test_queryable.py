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
        self.collection = self.client["whl-data"][LeagueModel.__collection_name__]

    def test_constructor(self):
        query = Queryable(self.collection, LeagueModel)
        self.assertIsInstance(query, Queryable)
        self.assertIsInstance(query.collection, pymongo.collection.Collection)

    def test_count(self):
        query = Queryable(self.collection, LeagueModel)
        count = query.count()
        self.assertEqual(1, query.count())

    def test_iterable(self):
        query = Queryable(self.client["whl-data"][LeagueModel.__collection_name__], LeagueModel)
        self.assertRaises(TypeError, query.__iter__, None)

    def test_select(self):
        query = Queryable(self.collection, LeagueModel).select(lambda x: x.short_name)
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("WHL", result[0][0])

    def test_select_list(self):
        query = Queryable(self.collection, LeagueModel).select(lambda x: [x.name, x.short_name])
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0][0])
        self.assertEqual("WHL", result[0][1])

    def test_select_tuple(self):
        query = Queryable(self.collection, LeagueModel).select(lambda x: (x.name, x.short_name))
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0][0])
        self.assertEqual("WHL", result[0][1])

    def test_select_dict(self):
        query = Queryable(self.collection, LeagueModel).select(lambda x: {
            "name": x.name,
            "short_name": x.short_name
        })
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0]["name"])
        self.assertEqual("WHL", result[0]["short_name"])

    def test_select_count(self):
        query = Queryable(self.collection, LeagueModel).select(lambda x: x.name).count()
        self.assertEqual(1, query)

    def test_to_list_exception(self):
        query = Queryable(self.collection, LeagueModel)
        self.assertRaises(TypeError, query.to_list)

    def test_to_list(self):
        query = Queryable(self.collection, LeagueModel).to_list()
        self.assertEqual("Western Hockey League", query[0].name)
        self.assertEqual(1, len(query[0].seasons))
