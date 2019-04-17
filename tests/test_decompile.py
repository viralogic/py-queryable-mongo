import ast
from unittest import TestCase
from py_linq_mongo.decompile import LambdaDecompiler


class TestDecompilers(TestCase):
    """
    Test cases for Decompiler abstract class
    """
    def test_simple_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name == "Western Hockey League").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')])))",
            ast.dump(tree)
        )

    def test_conjuction_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name == "Western Hockey League" and x.short_name == "WHL").__code__)
        print(ast.dump(tree))
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=And(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='short_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='WHL')])])))",
            ast.dump(tree)
        )
