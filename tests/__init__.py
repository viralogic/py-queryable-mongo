from py_linq_mongo.model import attributes


class LeagueModel(object):
    __collection_name__ = "team"

    id = attributes.ObjectId()
    name = attributes.String("name")
    short_name = attributes.String("short_name")


class SaleModel(object):
    __collection_name__ = "sales"

    id = attributes.ObjectId()
    item = attributes.String("item")
    price = attributes.Integer("price")
    quantity = attributes.Integer("quantity")
    date = attributes.DateTime("date")


class InvalidAttributeModel(object):
    __invalid_name__ = "team"


class EmptyCollectionNameModel(object):
    __collection_name__ = None
