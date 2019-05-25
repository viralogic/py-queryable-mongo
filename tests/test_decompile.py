import ast
from unittest import TestCase
from py_linq_mongo.decompile import LambdaDecompiler


class TestDecompilers(TestCase):
    """
    Test cases for Decompiler abstract class
    """
    def setUp(self):
        self.maxDiff = None

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

    def test_and_complex(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.gpa >= 10 and x.gpa <= 50 and x.last_name == "Fenske").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=And(), values=[BoolOp(op=And(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[GtE()], comparators=[Num(n=10)]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[LtE()], comparators=[Num(n=50)])]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='last_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Fenske')])])))",
            ast.dump(tree)
        )

    def test_or_lambda(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name == "Western Hockey League" or x.short_name == "WHL").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=Or(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Western Hockey League')]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='short_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='WHL')])])))",
            ast.dump(tree)
        )

    def test_or_complex(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.gpa >= 10 or x.gpa <= 50 or x.last_name == "Fenske").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=Or(), values=[BoolOp(op=Or(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[GtE()], comparators=[Num(n=10)]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[LtE()], comparators=[Num(n=50)])]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='last_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Fenske')])])))",
            ast.dump(tree)
        )

    def test_and_or_complex(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.gpa >= 10 and x.gpa <= 50 or x.last_name == "Fenske").__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BoolOp(op=Or(), values=[BoolOp(op=And(), values=[Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[GtE()], comparators=[Num(n=10)]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[LtE()], comparators=[Num(n=50)])]), Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='last_name', ctx=Load()), ops=[Eq()], comparators=[Str(s='Fenske')])])))",
            ast.dump(tree)
        )

    def test_tuple(self):
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
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: {
            'name': x.name,
            'season': x.season
        }).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=Dict(keys=[Str(s='name'), Str(s='season')], values=[Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), Attribute(value=Name(id='x', ctx=Load()), attr='season', ctx=Load())])))",
            ast.dump(tree)
        )

    def test_in(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.name in ['Western Hockey League']).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='name', ctx=Load()), ops=[In()], comparators=[Tuple(elts=[Str(s='Western Hockey League')], ctx=Load())])))",
            ast.dump(tree)
        )

    def test_add(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.goals + x.assists).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BinOp(left=Attribute(value=Name(id='x', ctx=Load()), attr='goals', ctx=Load()), op=Add(), right=Attribute(value=Name(id='x', ctx=Load()), attr='assists', ctx=Load()))))",
            ast.dump(tree)
        )

    def test_div(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.goals_against / x.games_played).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BinOp(left=Attribute(value=Name(id='x', ctx=Load()), attr='goals_against', ctx=Load()), op=Div(), right=Attribute(value=Name(id='x', ctx=Load()), attr='games_played', ctx=Load()))))",
            ast.dump(tree)
        )

    def test_minus(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.points - x.assists).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BinOp(left=Attribute(value=Name(id='x', ctx=Load()), attr='points', ctx=Load()), op=Sub(), right=Attribute(value=Name(id='x', ctx=Load()), attr='assists', ctx=Load()))))",
            ast.dump(tree)
        )

    def test_mod(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.goals_against % x.games_played).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BinOp(left=Attribute(value=Name(id='x', ctx=Load()), attr='goals_against', ctx=Load()), op=Mod(), right=Attribute(value=Name(id='x', ctx=Load()), attr='games_played', ctx=Load()))))",
            ast.dump(tree)
        )

    def test_mult(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: x.points * x.assists).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=BinOp(left=Attribute(value=Name(id='x', ctx=Load()), attr='points', ctx=Load()), op=Mult(), right=Attribute(value=Name(id='x', ctx=Load()), attr='assists', ctx=Load()))))",
            ast.dump(tree)
        )

    def test_unary_not(self):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile((lambda x: not x.gpa == 10).__code__)
        self.assertEqual(
            "Lambda(args=arguments(args=[Name(id='x', ctx=Param())], vararg=None, kwarg=None, defaults=[]), body=Return(value=UnaryOp(op=Not(), operand=Compare(left=Attribute(value=Name(id='x', ctx=Load()), attr='gpa', ctx=Load()), ops=[Eq()], comparators=[Num(n=10)]))))",
            ast.dump(tree)
        )
