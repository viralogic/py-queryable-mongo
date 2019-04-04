from unittest import TestCase
from py_linq_mongo.syntax_tree import CollectionLambdaTranslator, LambdaExpression
import ast


class TestLambdaAst(TestCase):
    """
    Unit tests for lambda expression AST
    """
    def setUp(self):
        self.translator = CollectionLambdaTranslator()

    def test_eq(self):
        tree = LambdaExpression.parse(lambda x: x.short_name == "WHL")
        print(ast.dump(tree))
