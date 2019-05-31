from unittest import TestCase
from pymongo import MongoClient
from py_linq_mongo.query import Queryable
from py_linq_mongo.provider import MongoProvider
from . import LeagueModel, EmptyCollectionNameModel, InvalidAttributeModel


class MongoProviderTests(TestCase):
    """
    Unit tests for the MongoProvider class
    """
    def setUp(self):
        self.provider = MongoProvider(uri="localhost:27017", db_name="whl-data", username="whl_user", password="Dawn381!")

    def test_invalid_models(self):
        self.assertRaises(AttributeError, self.provider.query, [InvalidAttributeModel])

    def test_empty_name(self):
        self.assertRaises(AttributeError, self.provider.query, [EmptyCollectionNameModel])

    def test_constructor(self):
        self.assertEqual(MongoClient, type(self.provider.connection))
        self.assertIsNotNone(self.provider.database)

    def test_query(self):
        query = self.provider.query(LeagueModel)
        self.assertIsInstance(query, Queryable)
        self.assertEqual(LeagueModel, query.model)
