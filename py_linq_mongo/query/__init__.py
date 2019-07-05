import pymongo
import json
import ast
import collections
from ..expressions import LambdaExpression
import abc
import py_linq
from py_linq import exceptions


class Queryable(object):
    """
    Class that encapsulates different methods to query a MongoDb collection
    """
    def __init__(self, collection, model):
        """
        Queryable constructor
        :param database: the connection to a MongoDb database
        :param model: instance of the model for the Mongo Collection
        """
        self.model = model
        self.collection = collection
        self.pipeline = []

    def __iter__(self):
        """
        Naive implementation of iterable. Checks if expression is an iterable.
        If so, yield a new instance of the model with results from the query.
        Otherwise, just returns none
        """
        for item in self.collection.aggregate(self.pipeline):
            yield type(self.model.__class__.__name__, (object,), item)

    def count(self):
        """
        Returns the number of documents in the collection
        return -> integer object
        """
        self.pipeline.append({"$count": "total"})
        query = self.collection.aggregate(self.pipeline)
        result = py_linq.Enumerable(query)
        return result.first()["total"] if result.count() > 0 else 0

    def select(self, func, include_id=False):
        """
        Projects each element of a document into a new form given by func

        func -> A projection function to apply to each element.

        return -> Queryable object
        """
        t = LambdaExpression.parse(func)
        if isinstance(t.body.value, ast.Name):
            return SimpleSelectQueryable(self.collection, self.pipeline, t.body, include_id)
        if isinstance(t.body.value, ast.Tuple) or isinstance(t.body.value, ast.List):
            return CollectionSelectQueryable(self.collection, self.pipeline, t.body, include_id)
        if isinstance(t.body.value, ast.Dict):
            return DictSelectQueryable(self.collection, self.pipeline, t.body, include_id)
        else:
            raise TypeError("Cannot project {0} node".format(t.body.value.__class__.__name__))

    def take(self, limit):
        self.pipeline.append({"$limit": limit})
        return self

    def skip(self, offset):
        self.pipeline.append({"$skip": offset})
        return self

    def where(self, func):
        t = LambdaExpression.parse(func)
        return WhereQueryable(self.collection, self.model, self.pipeline, t.body)

    # def max(self, func=None):
    #     if func is None:
    #         return self.as_enumerable().max()
    #     t = LambdaExpression.parse(func)
    #     if not isinstance(t.body.value, ast.Name):
    #         raise TypeError("Must select a property of {0}".format(self.model.__class__.__name__))
    #     v = self.order_by_descending(func).first_or_default()
    #     return None if v is None else func(v)

    # def min(self, func=None):
    #     query = Queryable(operators.MinOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def sum(self, func=None):
    #     query = Queryable(operators.SumOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def average(self, func=None):
    #     query = Queryable(operators.AveOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    def any(self, func=None):
        """
        Determines whether a sequence contains any elements that satisfy a given predicate
        func -> lambda expression used to filter a sequence
        return -> True if sequence does contain elements else False
        """
        return self.count() > 0 if func is None else self.where(func).count() > 0

    def all(self, func=None):
        """
        Determines whether all elements in a sequence satisfy a given condition
        func => lambda expression used to filter a sequence
        return -> True if all elements in the sequence satisfy a given predicate otherwise False
        """
        if func is None:
            return True
        predicate_count = self.where(func).count()
        count = self.count()
        return predicate_count == count

    def first(self, func=None):
        if func is not None:
            return self.where(func).take(1).as_enumerable().first()
        return self.take(1).as_enumerable().first()

    def first_or_default(self, func=None):
        try:
            return self.first(func)
        except exceptions.NoElementsError:
            return None

    def order_by(self, func):
        t = LambdaExpression.parse(func)
        return OrderedQueryable(self.collection, self.model, self.pipeline, t.body, 1)

    def order_by_descending(self, func):
        t = LambdaExpression.parse(func)
        return OrderedQueryable(self.collection, self.model, self.pipeline, t.body, -1)

    def single(self, func=None):
        if func is None:
            result = self
        else:
            result = self.where(func)
        result = result.take(2).to_list()
        if len(result) == 0:
            raise exceptions.NoMatchingElement(u"No matching elements could be found")
        if len(result) > 1:
            raise exceptions.MoreThanOneMatchingElement(u"More than one matching element found")
        return result[0]

    def single_or_default(self, func=None):
        try:
            return self.single(func)
        except exceptions.NoMatchingElement:
            return None

    def as_enumerable(self):
        return py_linq.Enumerable(self)

    def to_list(self):
        return self.as_enumerable().to_list()


class SelectQueryable(abc.ABC, Queryable):
    """
    Abstract class for select queryable
    """
    def __init__(self, collection, pipeline, node, include_id):
        self.include_id = include_id
        self.node = node
        self.pipeline = py_linq.Enumerable(pipeline).add(self.projection).to_list()
        self.collection = collection

    @abc.abstractproperty
    def projection(self):
        raise NotImplementedError()


class SimpleSelectQueryable(SelectQueryable):
    """
    Performs a projection of a collection when ast.Name is encountered
    """
    def __init__(self, collection, pipeline, node, include_id=False):
        super(SimpleSelectQueryable, self).__init__(collection, pipeline, node, include_id)

    @property
    def projection(self):
        project = {
            "$project": {
                "_id": 1 if self.include_id else 0
            }
        }
        project["$project"][self.node.mongo] = "${0}".format(self.node.mongo)
        return project

    def __iter__(self):
        for e in self.collection.aggregate(self.pipeline):
            yield tuple([v for k, v in e.items()])


class DictSelectQueryable(SelectQueryable):
    """
    Performs a projection of a collection
    """
    def __init__(self, collection, pipeline, node, include_id=False):
        super(DictSelectQueryable, self).__init__(collection, pipeline, node, include_id)

    @property
    def projection(self):
        project = json.loads(self.node.mongo)
        project["$project"]["_id"] = 1 if self.include_id else 0
        return project

    def __iter__(self):
        return self.collection.aggregate(self.pipeline).__iter__()


class CollectionSelectQueryable(DictSelectQueryable):
    """
    Performs a projection of a collection when ast.Tuple or ast.List is encountered
    """
    def __init__(self, collection, pipeline, node, include_id=False):
        super(CollectionSelectQueryable, self).__init__(collection, pipeline, node, include_id)

    def __iter__(self):
        for e in self.collection.aggregate(self.pipeline):
            yield tuple([v for k, v in e.items()])


class OrderedQueryable(Queryable):
    """
    Sorts a collection
    """
    def __init__(self, collection, model, pipeline, node, direction=1):
        super(OrderedQueryable, self).__init__(collection, model)
        self.pipeline = pipeline
        self.node = node
        self.sort_dict = {"$sort": {}}
        self.sort_dict["$sort"][self.node.mongo] = direction

    def __iter__(self):
        self.pipeline.append(self.sort_dict)
        for item in self.collection.aggregate(self.pipeline):
            i = type(self.model.__class__.__name__, (object,), item)
            yield i

    def _addSortKey(self, func, direction):
        t = LambdaExpression.parse(func)
        if not isinstance(t.body.value, ast.Name):
            raise TypeError("Lambda function needs to select a field")
        self.sort_dict["$sort"][t.body.mongo] = direction

    def then_by(self, func):
        self._addSortKey(func, 1)
        return self

    def then_by_descending(self, func):
        self._addSortKey(func, -1)
        return self


class WhereQueryable(Queryable):
    """
    Filters a collection
    """
    def __init__(self, collection, model, pipeline, node):
        super(WhereQueryable, self).__init__(collection, model)
        self.pipeline = pipeline.copy()
        self.node = node
        self.filter_dict = {}
        self.filter_dict["$match"] = json.loads(self.node.mongo)
        self.pipeline.append(self.filter_dict)

    def __iter__(self):
        for item in self.collection.aggregate(self.pipeline):
            i = type(self.model.__class__.__name__, (object,), item)
            yield i

    def where(self, func):
        fd = self.pipeline.remove(self.filter_dict)
        t = LambdaExpression.parse(func)
        j = json.loads(t.body.mongo)
        if "$and" in self.filter_dict["$match"]:
            self.filter_dict["$match"]["$and"].append(j)
        else:
            q = {"$and": [self.filter_dict["$match"], j]}
            self.filter_dict["$match"] = q
        self.pipeline.append(self.filter_dict)
        return self
