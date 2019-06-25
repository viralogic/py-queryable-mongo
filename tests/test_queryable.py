from unittest import TestCase
import pymongo
from py_linq_mongo.query import Queryable
import datetime
from . import SaleModel, LeagueModel, InvalidAttributeModel, EmptyCollectionNameModel
from py_linq import exceptions


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
        self.sales_collection = self.client["whl-data"][SaleModel.__collection_name__]

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

    def test_to_list(self):
        query = Queryable(self.collection, LeagueModel).to_list()
        self.assertEqual("Western Hockey League", query[0].name)
        self.assertEqual(1, len(query[0].seasons))

    def test_take(self):
        query = Queryable(self.collection, LeagueModel).take(1)
        self.assertEqual(1, len(query.to_list()))
        self.assertEqual("Western Hockey League", query.to_list()[0].name)

        query = Queryable(self.sales_collection, SaleModel).take(1)
        self.assertEqual(1, len(query.to_list()))
        self.assertEqual(10, query.to_list()[0].price)

    def test_skip(self):
        query = Queryable(self.collection, LeagueModel).skip(1)
        self.assertEqual(0, len(query.to_list()))

    def test_skip_take(self):
        query = Queryable(self.collection, LeagueModel).skip(1).take(1)
        self.assertEqual(0, len(query.to_list()))

    def test_take_skip(self):
        query = Queryable(self.collection, LeagueModel).take(1).skip(1)
        self.assertEqual(0, len(query.to_list()))

    def test_order_by(self):
        query = Queryable(self.sales_collection, SaleModel).order_by(lambda s: s.price).to_list()[0]
        self.assertEqual(5, query.price)

    def test_order_by_descending(self):
        query = Queryable(self.sales_collection, SaleModel).order_by_descending(lambda s: s.price).to_list()[0]
        self.assertEqual(20, query.price)

    def test_order_by_then_by(self):
        query = Queryable(self.sales_collection, SaleModel).order_by(lambda s: s.price).then_by(lambda s: s.date).to_list()[0]
        self.assertEqual(5, query.price)
        self.assertEqual(datetime.datetime(2014, 2, 3, 9, 5), query.date)

    def test_order_by_then_by_descending(self):
        query = Queryable(self.sales_collection, SaleModel).order_by(lambda s: s.price).then_by_descending(lambda s: s.date).to_list()[0]
        self.assertEqual(5, query.price)
        self.assertEqual(datetime.datetime(2014, 2, 15, 9, 5), query.date)

    def test_order_by_descending_then_by(self):
        query = Queryable(self.sales_collection, SaleModel).order_by_descending(lambda s: s.price).then_by(lambda s: s.quantity).to_list()[0]
        self.assertEqual(20, query.price)
        self.assertEqual(1, query.quantity)

    def test_order_by_descending_then_by_descending(self):
        query = Queryable(self.sales_collection, SaleModel).order_by_descending(lambda s: s.price).then_by_descending(lambda s: s.quantity).to_list()[0]
        self.assertEqual(20, query.price)
        self.assertEqual(1, query.quantity)

    def test_where(self):
        query = Queryable(self.sales_collection, SaleModel).where(lambda s: s.price > 5).to_list()
        self.assertEqual(3, len(query))

        query = Queryable(self.sales_collection, SaleModel).where(lambda s: s.item == "jkl").to_list()
        self.assertEqual(1, len(query))

    def test_combining_wheres(self):
        query = Queryable(self.sales_collection, SaleModel).where(lambda s: s.price > 5).where(lambda s: s.item == "abc").to_list()
        self.assertEqual(2, len(query))

    def test_first(self):
        query = Queryable(self.sales_collection, SaleModel).order_by(lambda s: s.date).first()
        self.assertEqual(datetime.datetime(2014, 1, 1, 8, 0), query.date)

    def test_single(self):
        query = Queryable(self.sales_collection, SaleModel).single(lambda s: s.item == "jkl")
        self.assertEqual(20, query.price)

    def test_no_first(self):
        query = Queryable(self.sales_collection, SaleModel).where(lambda s: s.price > 20)
        self.assertRaises(exceptions.NoElementsError, query.first, None)

    def test_no_single(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(exceptions.NoMatchingElement, query.single, lambda s: s.price > 20)

    def test_more_than_one_single(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(exceptions.MoreThanOneMatchingElement, query.single, lambda s: s.item == "abc")

    def test_first_or_default(self):
        query = Queryable(self.sales_collection, SaleModel).order_by(lambda s: s.date).first_or_default()
        self.assertIsNotNone(query)
        self.assertEqual(datetime.datetime(2014, 1, 1, 8, 0), query.date)

    def test_no_first_or_default(self):
        query = Queryable(self.sales_collection, SaleModel).where(lambda s: s.price > 20).first_or_default()
        self.assertIsNone(query)

    def test_single_or_default(self):
        raise NotImplementedError()

    def test_no_single_or_default(self):
        raise NotImplementedError()
