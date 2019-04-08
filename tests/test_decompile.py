from unittest import TestCase
from py_linq_mongo.decompile import LambdaDecompiler


class TestDecompilers(TestCase):
    """
    Test cases for Decompiler abstract class
    """
    def test_lambda(self):
        f = lambda x: x.name == "Western Hockey League"
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile(f.__code__)

