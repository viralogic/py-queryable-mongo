from unittest import TestCase
import mongomock
from py_linq_mongo.query import Queryable
import datetime
from . import SaleModel, LeagueModel, StudentModel
from py_linq import exceptions
from .data import MongoData


class QueryableTests(TestCase):
    """
    Unit tests for Queryable class
    """

    def setUp(self):
        """
        Sets up query to collection
        """
        self.client = mongomock.MongoClient()
        self.db = self.client["whl-data"]
        seeder = MongoData(self.db)
        seeder.seed_data()
        self.collection = self.db[LeagueModel.__collection_name__]
        self.sales_collection = self.db[SaleModel.__collection_name__]
        self.students_collection = self.db[StudentModel.__collection_name__]

    def test_count(self):
        query = Queryable(self.collection, LeagueModel)
        self.assertEqual(1, query.count())

    def test_iterable(self):
        query = Queryable(
            self.client["whl-data"][LeagueModel.__collection_name__],
            LeagueModel,
        )
        self.assertRaises(TypeError, query.__iter__, None)

    def test_select(self):
        query = Queryable(self.collection, LeagueModel).select(
            lambda x: x.short_name
        )
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("WHL", result[0][0])

    def test_select_list(self):
        query = Queryable(self.collection, LeagueModel).select(
            lambda x: [x.name, x.short_name]
        )
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0][0])
        self.assertEqual("WHL", result[0][1])

    def test_select_tuple(self):
        query = Queryable(self.collection, LeagueModel).select(
            lambda x: (x.name, x.short_name)
        )
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0][0])
        self.assertEqual("WHL", result[0][1])

    def test_select_dict(self):
        query = Queryable(self.collection, LeagueModel).select(
            lambda x: {"name": x.name, "short_name": x.short_name}
        )
        result = list(query)
        self.assertEqual(1, len(result))
        self.assertEqual("Western Hockey League", result[0]["name"])
        self.assertEqual("WHL", result[0]["short_name"])

    def test_select_count(self):
        query = (
            Queryable(self.collection, LeagueModel)
            .select(lambda x: x.name)
            .count()
        )
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
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.price)
            .to_list()[0]
        )
        self.assertEqual(5, query.price)

    def test_order_by_descending(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by_descending(lambda s: s.price)
            .to_list()[0]
        )
        self.assertEqual(20, query.price)

    def test_order_by_then_by(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.price)
            .then_by(lambda s: s.date)
            .to_list()[0]
        )
        self.assertEqual(5, query.price)
        self.assertEqual(datetime.datetime(2014, 2, 3, 9, 5), query.date)

    def test_order_by_then_by_descending(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.price)
            .then_by_descending(lambda s: s.date)
            .to_list()[0]
        )
        self.assertEqual(5, query.price)
        self.assertEqual(datetime.datetime(2014, 2, 15, 9, 5), query.date)

    def test_order_by_descending_then_by(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by_descending(lambda s: s.price)
            .then_by(lambda s: s.quantity)
            .to_list()[0]
        )
        self.assertEqual(20, query.price)
        self.assertEqual(1, query.quantity)

    def test_order_by_descending_then_by_descending(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by_descending(lambda s: s.price)
            .then_by_descending(lambda s: s.quantity)
            .to_list()[0]
        )
        self.assertEqual(20, query.price)
        self.assertEqual(1, query.quantity)

    def test_where(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.price > 5)
            .to_list()
        )
        self.assertEqual(3, len(query))

        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.item == "jkl")
            .to_list()
        )
        self.assertEqual(1, len(query))

    def test_combining_wheres(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.price > 5)
            .where(lambda s: s.item == "abc")
            .to_list()
        )
        self.assertEqual(2, len(query))

    def test_first(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.date)
            .first()
        )
        self.assertEqual(datetime.datetime(2014, 1, 1, 8, 0), query.date)

        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.date)
            .first(lambda s: s.item == "jkl")
        )
        self.assertEqual(20, query.price)

    def test_single(self):
        query = Queryable(self.sales_collection, SaleModel).single(
            lambda s: s.item == "jkl"
        )
        self.assertEqual(20, query.price)

    def test_no_first(self):
        query = Queryable(self.sales_collection, SaleModel).where(
            lambda s: s.price > 20
        )
        self.assertRaises(exceptions.NoElementsError, query.first, None)

    def test_no_single(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(
            exceptions.NoMatchingElement, query.single, lambda s: s.price > 20
        )

    def test_more_than_one_single(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(
            exceptions.MoreThanOneMatchingElement,
            query.single,
            lambda s: s.item == "abc",
        )

    def test_first_or_default(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.date)
            .first_or_default()
        )
        self.assertIsNotNone(query)
        self.assertEqual(datetime.datetime(2014, 1, 1, 8, 0), query.date)

    def test_no_first_or_default(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.price > 20)
            .first_or_default()
        )
        self.assertIsNone(query)

        query = Queryable(self.sales_collection, SaleModel).first_or_default(
            lambda s: s.price > 20
        )
        self.assertIsNone(query)

    def test_single_or_default(self):
        query = Queryable(self.sales_collection, SaleModel).single_or_default(
            lambda s: s.item == "jkl"
        )
        self.assertIsNotNone(query)
        self.assertEqual("jkl", query.item)

    def test_no_single_or_default(self):
        query = Queryable(self.sales_collection, SaleModel).single_or_default(
            lambda s: s.price > 20
        )
        self.assertIsNone(query)

    def test_any(self):
        query = Queryable(self.sales_collection, SaleModel).any()
        self.assertTrue(query)

    def test_any_predicate(self):
        query = Queryable(self.sales_collection, SaleModel).any(
            lambda s: s.item == "jkl"
        )
        self.assertTrue(query)

        query = Queryable(self.sales_collection, SaleModel).any(
            lambda s: s.price > 20
        )
        self.assertFalse(query)

    def test_all_predicate_no_lambda(self):
        query = Queryable(self.sales_collection, SaleModel).all()
        self.assertTrue(query)

    def test_all_predicate(self):
        query = Queryable(self.sales_collection, SaleModel).all(
            lambda s: s.quantity >= 1
        )
        self.assertTrue(query)

    def test_all_predicate_only_one(self):
        query = Queryable(self.sales_collection, SaleModel).all(
            lambda s: s.price >= 20
        )
        self.assertFalse(query)

    def test_max_selector(self):
        query = Queryable(self.sales_collection, SaleModel).max(
            lambda s: s.price
        )
        self.assertEqual(20, query)

    def test_min_selector(self):
        query = Queryable(self.sales_collection, SaleModel).min(
            lambda s: s.price
        )
        self.assertEqual(5, query)

    def test_max_no_selector(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(AttributeError, query.max)
        self.assertRaises(TypeError, query.max, lambda s: s.price < 20)

    def test_min_no_selector(self):
        query = Queryable(self.sales_collection, SaleModel)
        self.assertRaises(AttributeError, query.min)
        self.assertRaises(TypeError, query.min, lambda s: s.price < 20)

    def test_max_select_array(self):
        query = Queryable(self.students_collection, StudentModel)
        self.assertRaises(TypeError, query.max, lambda s: s.labs)

    def test_min_select_array(self):
        query = Queryable(self.students_collection, StudentModel)
        self.assertRaises(TypeError, query.min, lambda s: s.labs)

    def test_sum_selector(self):
        query = Queryable(self.sales_collection, SaleModel).sum(
            lambda s: s.quantity
        )
        self.assertEqual(28, query)

    def test_avg_selector(self):
        query = Queryable(self.sales_collection, SaleModel).average(
            lambda s: s.quantity
        )
        avg = 28 / 5
        self.assertEqual(avg, query)
