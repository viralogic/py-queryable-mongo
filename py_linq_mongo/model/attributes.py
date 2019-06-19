import pymongo
from datetime import datetime


class ModelAttribute(object):
    def __init__(self, attribute_type, name):
        """
        Default Constructor
        :param attribute type: The object type of the attribute
        :param name: The name of the attribute in the Mongo DB document
        """
        self.attribute_type = attribute_type
        if not type(name) is str:
            raise TypeError("name argument must be a string")
        self.name = name


class ObjectId(ModelAttribute):
    def __init__(self, name="_id"):
        """
        Attribute used to model the ObjectId attribute of a document
        :param name: The name of the ObjectId attribute
        """
        super(ObjectId, self).__init__(pymongo.collection.ObjectId, name)


class String(ModelAttribute):
    def __init__(self, name):
        """
        Attribute used to model a string attribute type of a document
        :param name: The name of the string attribute in the MongoDB document
        """
        super(String, self).__init__(str, name)


class Integer(ModelAttribute):
    def __init__(self, name):
        """
        Attribute used to model an integer attribute type of a document
        :param name: The name of the integer attribute in the MongoDB document
        """
        super(Integer, self).__init__(int, name)


class DateTime(ModelAttribute):
    def __init__(self, name):
        """
        Attribute used to model a date attribute type of a document
        :param name -> The name of the date attribute in the MongoDB document
        """
        super(DateTime, self).__init__(datetime, name)
