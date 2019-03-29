import inspect


class Queryable(object):
    """
    Class that encapsulates different methods to query a MongoDb collection
    """
    def __init__(self, connection, collection_type):
        """
        Queryable constructor
        :param connection The connection to a MongoDb database
        :param collection_type The MongoModel collection type
        """
        self.connection = connection
        if not hasattr(, "__collection_name__"):
            raise AttributeError("__collection_name__ attribute not found in MongoModel")
        if is_null_or_empty(collection.__collection_name__):
            raise AttributeError("__collection_name__ must be set")
        self.collection_type = collection_type
