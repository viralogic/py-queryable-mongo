import json
import ast
from ..expressions import LambdaExpression
import abc
import py_linq
from py_linq import exceptions
from py_linq import core
from collections import deque


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

    def next(self):
        item = next(self.collection.aggregate(self.pipeline))
        return type(self.model.__class__.__name__, (object, ), item)

    def __next__(self):
        return self.next()

    def count(self):
        """
        Returns the number of documents in the collection
        return -> integer object
        """
        self.pipeline.append({"$count": "total"})
        query = list(self.collection.aggregate(self.pipeline))
        return query[0]["total"]

    def select(self, func, include_id=False):
        """
        Projects each element of a document into a new form given by func
        func -> A projection function to apply to each element.
        return -> Queryable object
        """
        t = LambdaExpression.parse(func)
        if isinstance(t.body.value, ast.Name):
            return SimpleSelectQueryable(
                self.collection, self.pipeline, t.body, include_id
            )
        if isinstance(t.body.value, ast.Tuple) or isinstance(
            t.body.value, ast.List
        ):
            return CollectionSelectQueryable(
                self.collection, self.pipeline, t.body, include_id
            )
        if isinstance(t.body.value, ast.Dict):
            return DictSelectQueryable(
                self.collection, self.pipeline, t.body, include_id
            )
        else:
            raise TypeError(
                "Cannot project {0} node".format(
                    t.body.value.__class__.__name__
                )
            )

    def take(self, limit):
        self.pipeline.append({"$limit": limit})
        return self

    def skip(self, offset):
        """
        """
        self.pipeline.append({"$skip": offset})
        return self

    def where(self, func):
        """
        Filters a sequence of elements by only returning the elements that satisfy a given predicate
        func -> predicate to filter sequence as a lambda function
        return -> Queryable object that only contains elements that satisfy the given predicate
        """
        t = LambdaExpression.parse(func)
        return WhereQueryable(
            self.collection, self.model, self.pipeline, t.body
        )

    def max(self, func=None):
        """
        Finds the maximum value. If a lambda function is given, then will find the maximum value for the
        given field.
        func -> selector for the field want to determine the maximum of as a lambda function
        return -> the maximum value as a scalar value
        """
        return ScalarSelectQueryable(
            self.collection, self.pipeline, "$max", func
        ).scalar

    def min(self, func=None):
        """
        Finds the minimum value. If a lambda function is given, then will find the minimum value for the
        given field.
        func -> selector for the field to determine the minimum of as a lambda function
        return -> the minimum value as a scalar value
        """
        return ScalarSelectQueryable(
            self.collection, self.pipeline, "$min", func
        ).scalar

    def sum(self, func=None):
        """
        Sums the values in a collection. If a lambda function is given, then it will sum only the values for
        the given field.
        func -> selector for the field to sum as a lambda function. Optional.
        return -> the sum of the values
        """
        return ScalarSelectQueryable(
            self.collection, self.pipeline, "$sum", func
        ).scalar

    def average(self, func=None):
        """
        Averages the values in a collection. If a lambda function is given, then it will average only the values
        for the given field.
        func -> selector for the field to average as a lambda function. Optional
        return -> the average of the values
        """
        return ScalarSelectQueryable(
            self.collection, self.pipeline, "$avg", func
        ).scalar

    def any(self, func=None):
        """
        Determines whether a sequence contains any elements that satisfy a given predicate
        func -> lambda expression used to filter a sequence
        return -> True if sequence does contain elements else False
        """
        return self.first_or_default(func) is not None

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
        
        result = self
        if func is not None:
            result = result.where(func).take(1)
        else:
            result = result.take(1)
        result = list(result)
        if not result:
            raise exceptions.NoElementsError()
        return result[0]

    def first_or_default(self, func=None):
        try:
            return self.first(func)
        except exceptions.NoElementsError:
            return None

    def order_by(self, func):
        t = LambdaExpression.parse(func)
        return OrderedQueryable(
            self.collection, self.model, self.pipeline, t.body, 1
        )

    def order_by_descending(self, func):
        t = LambdaExpression.parse(func)
        return OrderedQueryable(
            self.collection, self.model, self.pipeline, t.body, -1
        )

    def single(self, func=None):
        if func is None:
            result = self
        else:
            result = self.where(func)
        result = result.take(2).to_list()
        if len(result) == 0:
            raise exceptions.NoMatchingElement(
                u"No matching elements could be found"
            )
        if len(result) > 1:
            raise exceptions.MoreThanOneMatchingElement(
                u"More than one matching element found"
            )
        return result[0]

    def single_or_default(self, func=None):
        try:
            return self.single(func)
        except exceptions.NoMatchingElement:
            return None

    def as_enumerable(self):
        return py_linq.Enumerable((item for item in self))

    def to_list(self):
        return self.as_enumerable().to_list()

    def aggregate(self, seed, func):
        """
        Applies an accumulator function over a sequence. The specified seed value is used
        as the initial accumulator value
        """
        return self.as_enumerable().aggregate(func, seed)

    def concat(self, sequence):
        """
        Concatenates two sequences
        """
        return self.as_enumerable().concat(sequence)

    def contains(self, item, func=None):
        """
        Determines whether an Queryable contains the given element
        """
        if func is not None:
            return self.any(lambda e: func(e) == item)
        return self.any(lambda e: e == item)

    def default_if_empty(self, value=None):
        """
        Returns the elements of the specified sequence or a singleton Enumerable collection containing None
        """
        return self if self.any() else py_linq.Enumerable().default_if_empty(value)

    def distinct(self, func=lambda x: x):
        """
        Returns distinct elements from a sequence. If a selector function is given, then
        then the function is used as a comparison function to compare equality
        """
        raise NotImplementedError()

    def element_at(self, index):
        """
        Gets the element at the given index
        """
        if not isinstance(index, int):
            raise TypeError("Must be an integer")
        try:
            return self.skip(index).first()
        except exceptions.NoElementsError:
            raise IndexError

    def element_at_or_default(self, index):
        """
        Gets the element at the given index or None if index is out of range
        """
        try:
            return self.element_at(index)
        except IndexError:
            return None

    def except_(self, queryable, func=lambda x: x):
        """
        Produces the set difference between two Queryable collections
        """
        raise NotImplementedError()

    def intersect(self, queryable, func=lambda x: x):
        """
        Produces the set intersection between two Queryable collections
        """
        raise NotImplementedError()

    def group_by(self, func=lambda x: x):
        """
        Groups the elements of a sequece by the given key
        """
        t = LambdaExpression.parse(func)
        return GroupedQueryable(
            self.collection, self.model, self.pipeline, t.body
        )

    def group_join(self, inner_collection, outer_key, inner_key, result_func):
        """
        Correlates the elements of two sequences based on key equality and groups the results.
        The default equality comparer is used to compare keys
        """
        raise NotImplementedError()

    def join(self, inner_collection, outer_key, inner_key, result_func):
        """
        Correlates the elements of two sequences based on matching keys
        """
        raise NotImplementedError()

    def last(self, func=None):
        """
        Returns the last element in a sequence
        """
        return self.reverse().first()

    def last_or_default(self, func=None):
        """
        Returns the last element of a sequence, or None if no element is found
        """
        return self.reverse().first_or_default(func)

    def reverse(self):
        """
        Inverts the order of the elements in a sequence
        """
        self.pipeline.append({
            "$sort": {
                "_id": -1
            }
        })
        return self

    def select_many(self, func=None):
        """
        Projects each element of a sequence to an IEnumerable<T> and
        combines the resulting sequences into one sequence of type Queryable
        """
        raise NotImplementedError()

    def sequence_equal(self, collection):
        """
        Determines whether two sequences are equal
        """
        raise NotImplementedError()

    def skip_while(self, predicate):
        """
        Bypasses elements in a sequence as long as a specified condition is true and
        then returns the remaining elements
        """
        raise NotImplementedError()

    def take_while(self, predicate):
        """
        Returns elements from a sequence as long as a specified condition is true,
        and then skips the remaining elements
        """
        raise NotImplementedError()

    def union(self, collection, func=None):
        """
        Produces the set union of two sequences by using a specified lambda function to evaluate
        equality
        """
        raise NotImplementedError()

    def zip(self, collection, func):
        """
        Merges two sequences by using the specified predicate function
        """
        raise NotImplementedError()


class SelectQueryable(abc.ABC, Queryable):
    """
    Abstract class for select queryable
    """

    def __init__(self, collection, pipeline, node, include_id):
        self.include_id = include_id
        self.node = node
        self.pipeline = [*pipeline, self.projection]
        self.collection = collection

    @abc.abstractproperty
    def projection(self):
        raise NotImplementedError()

    def reverse(self):
        return self.as_enumerable().reverse()


class SimpleSelectQueryable(SelectQueryable):
    """
    Performs a projection of a collection when ast.Name is encountered
    """

    def __init__(self, collection, pipeline, node, include_id=False):
        super(SimpleSelectQueryable, self).__init__(
            collection, pipeline, node, include_id
        )

    @property
    def projection(self):
        project = {"$project": {"_id": 1 if self.include_id else 0}}
        project["$project"][self.node.mongo] = "${0}".format(self.node.mongo)
        return project

    def __iter__(self):
        for e in self.collection.aggregate(self.pipeline):
            yield tuple([v for k, v in e.items()])

    def next(self):
        e = next(self.collection.aggregate(self.pipeline))
        return tuple([v for k, v in e.items()])

    def __next__(self):
        return self.next()


class ScalarSelectQueryable(object):
    """
    Performs projection of a collection using scalar operator
    """

    def __init__(self, collection, pipeline, operator, func):
        """
        Constructor for a projection of collection to scalar
        collection -> the collection that is being queried
        pipeline -> the aggregate pipeline as a list
        operator -> the Mongo scalar operator $min, $max, etc
        func -> lambda function as a selector
        """
        self.operator = operator
        self.func = func
        self.collection = collection
        t = None if self.func is None else LambdaExpression.parse(func)
        if not isinstance(t.body.value, ast.Name):
            raise TypeError("lambda function must select a property")
        self.node = t.body
        self.pipeline = [*pipeline, self.grouping]

    @property
    def grouping(self):
        if self.node is None:
            return
        grouping = {"$group": {"_id": None, "value": {}}}
        grouping["$group"]["value"][self.operator] = "${0}".format(
            self.node.mongo
        )
        return grouping

    @property
    def scalar(self):
        o = list(self.collection.aggregate(self.pipeline))[0]
        m = o["value"]
        if hasattr(m, "__iter__"):
            raise TypeError(
                "Please use select_many before calling a scalar operator"
            )
        return m


class DictSelectQueryable(SelectQueryable):
    """
    Performs a projection of a collection
    """

    def __init__(self, collection, pipeline, node, include_id=False):
        super(DictSelectQueryable, self).__init__(
            collection, pipeline, node, include_id
        )

    @property
    def projection(self):
        project = json.loads(self.node.mongo)
        project["$project"]["_id"] = 1 if self.include_id else 0
        return project

    def __iter__(self):
        return self.collection.aggregate(self.pipeline).__iter__()

    def next(self):
        return next(self.collection.aggregate(self.pipeline))

    def __next__(self):
        return self.next()


class CollectionSelectQueryable(DictSelectQueryable):
    """
    Performs a projection of a collection when ast.Tuple or ast.List is encountered
    """

    def __init__(self, collection, pipeline, node, include_id=False):
        super(CollectionSelectQueryable, self).__init__(
            collection, pipeline, node, include_id
        )

    def __iter__(self):
        for e in self.collection.aggregate(self.pipeline):
            yield tuple([v for k, v in e.items()])

    def next(self):
        e = next(self.collection.aggregate(self.pipeline))
        return tuple([v for k, v in e.items()])

    def __next__(self):
        return self.next()


class OrderedQueryable(Queryable):
    """
    Sorts a collection
    """

    def __init__(self, collection, model, pipeline, node, direction=1):
        super(OrderedQueryable, self).__init__(collection, model)
        self.pipeline = pipeline
        self.node = node
        self.direction = direction
        self.sort_dict = {"$sort": {}}
        self.sort_dict["$sort"][self.node.mongo] = self.direction

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

    def reverse(self):
        return self.as_enumerable().reverse()


class WhereQueryable(Queryable):
    """
    Filters a collection
    """

    def __init__(self, collection, model, pipeline, node):
        super(WhereQueryable, self).__init__(collection, model)
        self.node = node
        self.filter_dict = {}
        self.filter_dict["$match"] = json.loads(self.node.mongo)
        self.pipeline = [*pipeline, self.filter_dict]

    def __iter__(self):
        for item in self.collection.aggregate(self.pipeline):
            i = type(self.model.__class__.__name__, (object,), item)
            yield i

    def where(self, func):
        self.pipeline.remove(self.filter_dict)
        t = LambdaExpression.parse(func)
        j = json.loads(t.body.mongo)
        if "$and" in self.filter_dict["$match"]:
            self.filter_dict["$match"]["$and"].append(j)
        else:
            q = {"$and": [self.filter_dict["$match"], j]}
            self.filter_dict["$match"] = q
        self.pipeline.append(self.filter_dict)
        return self


class GroupedQueryable(Queryable):
    """
    Groups a collection based on given key
    """
    def __init__(self, collection, model, pipeline, node):
        super(GroupedQueryable, self).__init__(collection, model)
        self.node = node
        self.group_dict = {
            "$group": {}
        }
        self.group_dict["$group"]["_id"] = "${0}".format(self.node.mongo)
        self.group_dict["$group"]["items"] = {
            "$push": "$$ROOT"
        }
        self.pipeline = [*pipeline, self.group_dict]

    def __iter__(self):
        for g in self.collection.aggregate(self.pipeline):
            k = {}
            k[self.node.mongo] = g["_id"]
            key = core.Key(k)
            data = []
            for i in g["items"]:
                element = type(self.model.__class__.__name__, (object,), i)
                data.append(element)
            yield py_linq.py_linq.Grouping(key, data)



    

    

