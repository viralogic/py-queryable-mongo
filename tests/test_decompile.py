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

    def test_and_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name == "Western Hockey League" and x.short_name == "WHL").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=And(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='short_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='WHL')])])))",
            ast.dump(tree)
        )

    def test_or_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name == "Western Hockey League" or x.short_name == "WHL").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=Or(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='short_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='WHL')])])))",
            ast.dump(tree)
        )

    def test_if_else_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: "WHL" if x.name == "Western Hockey League" else "NOT WHL").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=IfExp(test=Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')]), body=Str(s='WHL'), orelse=Str(s='NOT WHL'))))",
            ast.dump(tree)
        )

    def test_tuple(self):
        self.maxDiff = None
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: (x.name, x.season)).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=Tuple(elts=[Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), Attribute(value=Name(id='x', ctx=Load()), attr='season', ctx=Load())], ctx=Load())))",
            ast.dump(tree)
        )

    def test_list(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: [x.name, x.season]).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=List(elts=[Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), Attribute(value=Name(id='x', ctx=Load()), attr='season', ctx=Load())], ctx=Load())))",
            ast.dump(tree)
        )

    def test_dict(self):
        self.maxDiff = None
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: {
            'name': x.name,
            'season': x.season
        }).__code__)
        print(ast.dump(tree))
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=Dict(keys=[Str(s='name'), Str(s='season')], values=[Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), Attribute(value=Name(id='x', ctx=Load()), attr='season', ctx=Load())])))",
            ast.dump(tree)
        )
