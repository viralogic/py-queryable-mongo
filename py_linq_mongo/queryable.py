import inspect
import pymongo


class Queryable(object):
    """
    Class that encapsulates different methods to query a MongoDb collection
    """
    def __init__(self, database, model):
        """
        Queryable constructor
        :param database the connection to a MongoDb database
        :param model type the collection type
        """
        self.database = database
        self.model = model
        if not hasattr(model, "__collection_name__"):
            raise AttributeError("Attribute __collection_name__ not found")
        if getattr(model, "__collection_name__") is None or len(getattr(model, "__collection_name__")) == 0:
            raise AttributeError("Attribute __collection_name__ needs to be set")
        self.expression = self.database[self.model.__collection_name__]

    def count(self):
        """
        Returns the number of documents in the collection
        :return: integer object
        """
        return self.expression.count_documents({})
