from unittest import TestCase
import mongomock
from py_linq_mongo.query import Queryable
import datetime
from . import (
    SaleModel,
    LeagueModel,
    StudentModel,
)
import py_linq
from py_linq import (
    exceptions,
)
from py_linq.py_linq import Grouping
from .data import MongoData
from py_linq_mongo.query import (
    GroupedQueryable,
)


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

        query = (
            Queryable(self.sales_collection, SaleModel)
            .select(lambda s: s.item)
            .first()
        )

        self.assertIsNotNone

    def test_last(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.date)
            .last()
        )
        self.assertEqual(datetime.datetime(year=2014, month=2, day=15, hour=9, minute=5, second=0), query.date)

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

    def test_no_last(self):
        query = Queryable(self.sales_collection, SaleModel).where(
            lambda s: s.price > 20
        )
        self.assertRaises(exceptions.NoElementsError, query.last, None)

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

    def test_last_or_default(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.date)
            .last_or_default()
        )
        self.assertIsNotNone(query)
        self.assertEqual(datetime.datetime(year=2014, month=2, day=15, hour=9, minute=5, second=0), query.date)

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

    def test_no_last_or_default(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.price > 20)
            .last_or_default()
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

    def test_default_if_empty(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .where(lambda s: s.item == "bwf")
            .default_if_empty()
        )
        self.assertIsNotNone(query)
        self.assertIsInstance(query, py_linq.Enumerable)
        self.assertEqual(1, query.count())
        self.assertIsNone(query.to_list()[0])

    def test_as_enumerable(self):
        query = Queryable(self.collection, LeagueModel).as_enumerable()
        self.assertEqual(1, query.count())
        league = query.first()
        self.assertIsNotNone(league)

    def test_aggregate(self):
        query = Queryable(self.sales_collection, SaleModel).aggregate(
            0, lambda result, item: result + item.price * item.quantity
        )
        self.assertEqual(215, query)

    def test_element_at_index_error(self):
        self.assertRaises(IndexError, Queryable(self.sales_collection, SaleModel).element_at, 5)

    def test_element_at_or_default_index_error(self):
        self.assertIsNone(Queryable(self.sales_collection, SaleModel).element_at_or_default(5))

    def test_element_at(self):
        self.assertEqual("xyz",Queryable(self.sales_collection, SaleModel).element_at(2).item)
        self.assertEqual("xyz", Queryable(self.sales_collection, SaleModel).element_at_or_default(2).item)

    def test_reverse_pre_select(self):
        truth = list(reversed(Queryable(self.sales_collection, SaleModel).select(lambda sc: sc.item).to_list()))
        test = Queryable(self.sales_collection, SaleModel).reverse().select(lambda sc: sc.item).to_list()
        self.assertListEqual(truth, test)

    def test_reverse_post_select_simple(self):
        truth = list(reversed(Queryable(self.sales_collection, SaleModel).select(lambda sc: sc.item).to_list()))
        test = Queryable(self.sales_collection, SaleModel).select(lambda sc: sc.item).reverse().to_list()
        self.assertListEqual(truth, test)

    def test_reverse_post_select_dict(self):
        truth = list(reversed(
            Queryable(self.sales_collection, SaleModel).select(lambda sc: {
                "item": sc.item,
                "price": sc.price
            }).to_list()
        ))
        test = Queryable(self.sales_collection, SaleModel).select(lambda sc: {
            "item": sc.item,
            "price": sc.price
        }).reverse().to_list()
        self.assertListEqual(truth, test)

    def test_reverse_post_select_list(self):
        truth = list(reversed(
            Queryable(self.sales_collection, SaleModel).select(lambda sc: [ sc.item, sc.price ]).to_list()
        ))
        test = Queryable(self.sales_collection, SaleModel).select(lambda sc: [ sc.item, sc.price ]).reverse().to_list()
        self.assertListEqual(truth, test)

    def test_reverse_post_select_tuple(self):
        truth = list(reversed(
            Queryable(self.sales_collection, SaleModel).select(lambda sc: ( sc.item, sc.price )).to_list()
        ))
        test = Queryable(self.sales_collection, SaleModel).select(lambda sc: ( sc.item, sc.price )).reverse().to_list()
        self.assertListEqual(truth, test)

    def test_order_by_reverse(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.price)
            .reverse()
            .to_list()[0]
        )
        self.assertEqual(20, query.price)

    def test_order_by_descending_reverse(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by_descending(lambda s: s.price)
            .reverse()
            .to_list()[0]
        )
        self.assertEqual(5, query.price)

    def test_order_by_then_by(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
            .order_by(lambda s: s.price)
            .then_by(lambda s: s.date)
            .reverse()
            .to_list()[3]
        )
        self.assertEqual(5, query.price)
        self.assertEqual(datetime.datetime(2014, 2, 15, 9, 5), query.date)

    def test_where_reverse(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
                .where(lambda sc: sc.item == "abc")
                .order_by(lambda sc: sc.quantity)
                .reverse()
                .to_list()[0]
        )
        self.assertEqual(10, query.quantity)

    def test_group_by(self):
        query = (
            Queryable(self.sales_collection, SaleModel)
                .group_by(lambda sc: sc.price)
        )
        self.assertIsInstance(query, GroupedQueryable)
        first_group = query.as_enumerable()\
            .order_by(lambda g: g.key.price).first()
        self.assertIsInstance(first_group, Grouping)
        self.assertEqual(5, first_group.first().price)

        last_group = query.as_enumerable()\
            .order_by_descending(lambda g: g.key.price).first()
        self.assertEqual(20, last_group.first().price)


