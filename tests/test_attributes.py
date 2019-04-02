from unittest import TestCase
from py_linq_mongo.model.attributes import ModelAttribute


class AttributeTests(TestCase):
    """
    Unit tests for different attribute types
    """
    def test_non_string_name(self):
        """
        Make sure that a TypeError is raised if name is not a string
        """
        self.assertRaises(TypeError, ModelAttribute, [str, 8])

    def test_name(self):
        """
        Make sure that the properties of the object id attribute are set
        """
        id = ModelAttribute(str, "_id")
        self.assertEqual("_id", id.name)
        self.assertEqual(str, id.attribute_type)
