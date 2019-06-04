import pymongo
import json
import ast
import collections
from ..expressions import LambdaExpression
import abc
import py_linq


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
        try:
            for item in self.collection:
                yield type(self.model.__class__.__name__, (object,), item)
        except:
            for item in self.collection.find({}):
                yield type(self.model.__class__.__name__, (object,), item)

    def count(self):
        """
        Returns the number of documents in the collection
        :return: integer object
        """
        self.pipeline.append({"$count": "total"})
        query = self.collection.aggregate(self.pipeline)
        for i in query:
            return i["total"]

    def select(self, func, include_id=False):
        """
        Projects each element of a document into a new form given by func
        :func: A projection function to apply to each element.
        :return: Queryable object
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
        return self.pipeline.append({"$limit": limit})

    # def skip(self, offset):
    #     return Queryable(operators.SkipOperator(self.expression, offset), self.provider)

    # def max(self, func=None):
    #     query = Queryable(operators.MaxOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def min(self, func=None):
    #     query = Queryable(operators.MinOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def sum(self, func=None):
    #     query = Queryable(operators.SumOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def average(self, func=None):
    #     query = Queryable(operators.AveOperator(self.expression, func), self.provider)
    #     return self.provider.db_provider.execute_scalar(query.sql)

    # def any(self, func=None):
    #     return self.count() > 0 if func is None else self.where(func).count() > 0

    # def all(self, func=None):
    #     if func is None:
    #         return True
    #     count = self.count()
    #     return self.where(func).count() == count

    # def first(self):
    #     return self.take(1).as_enumerable().first()

    # def first_or_default(self):
    #     try:
    #         return self.first()
    #     except NoElementsError:
    #         return None

    # def order_by(self, func):
    #     return OrderedQueryable(operators.OrderByOperator(self.expression, func), self.provider)

    # def order_by_descending(self, func):
    #     return OrderedQueryable(operators.OrderByDescendingOperator(self.expression, func), self.provider)

    # def where(self, func):
    #     return Queryable(operators.WhereOperator(self.expression, func), self.provider)

    # def single(self, func=None):
    #     result = self.where(func).to_list() if func is not None else self.to_list()
    #     count = len(result)
    #     if count == 0:
    #         raise NoMatchingElement(u"No matching elements could be found")
    #     if count > 1:
    #         raise MoreThanOneMatchingElement(u"More than one matching element found")
    #     return result[0]

    # def single_or_default(self, func=None):
    #     try:
    #         return self.single(func)
    #     except NoMatchingElement:
    #         return None

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
