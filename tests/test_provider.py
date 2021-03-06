from unittest import TestCase
import mongomock
from py_linq_mongo.query import Queryable
from py_linq_mongo.provider import MongoProvider
from . import LeagueModel, EmptyCollectionNameModel, InvalidAttributeModel


class MongoProviderTests(TestCase):
    """
    Unit tests for the MongoProvider class
    """

    def setUp(self):
        self.provider = MongoProvider(
            mongomock.MongoClient(), db_name="whl-data"
        )

    def test_invalid_models(self):
        self.assertRaises(
            AttributeError, self.provider.query, [InvalidAttributeModel]
        )

    def test_empty_name(self):
        self.assertRaises(
            AttributeError, self.provider.query, [EmptyCollectionNameModel]
        )

    def test_constructor(self):
        self.assertIsNotNone(self.provider.database)

    def test_constructor_exception(self):
        self.assertRaises(
            AttributeError, self.provider.query, InvalidAttributeModel
        )
        self.assertRaises(
            AttributeError, self.provider.query, EmptyCollectionNameModel
        )

    def test_query(self):
        query = self.provider.query(LeagueModel)
        self.assertIsInstance(query, Queryable)
        self.assertEqual(LeagueModel, query.model)
