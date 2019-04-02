from py_linq_mongo.model.attributes import ObjectId, String


class LeagueModel(object):
    __collection_name__ = "team"

    id = ObjectId()
    name = String("name")
    short_name = String("short_name")


class InvalidAttributeModel(object):
    __invalid_name__ = "team"


class EmptyCollectionNameModel(object):
    __collection_name__ = None
