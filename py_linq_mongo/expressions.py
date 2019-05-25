import ast
import json
import py
from .decompile import LambdaDecompiler


class LambdaExpression(object):

    """
    Parses a Python lambda expression and returns a modified AST that contains
    appropriate Mongo syntax
    """
    @staticmethod
    def parse(func):
        decompiler = LambdaDecompiler()
        tree = decompiler.decompile(func.__code__)
        translator = CollectionLambdaTranslator()
        translator.generic_visit(tree)
        return tree


class CollectionLambdaTranslator(ast.NodeVisitor):
    """
    Visitor for converting lambda expressions into Mongo query
    """
    def __init__(self):
        """
        Default constructor
        :param collection_type: The Model type
        """
        super(CollectionLambdaTranslator, self).__init__()

    def visit_Return(self, node):
        self.generic_visit(node)
        attr_node = getattr(node, "value")
        members = attr_node.__dict__.keys()
        for a in members:
            setattr(node, a, getattr(attr_node, a))

    def visit_Eq(self, node):
        node.mongo = "$eq"

    def visit_LtE(self, node):
        node.mongo = "$lte"

    def visit_GtE(self, node):
        node.mongo = "$gte"

    def visit_Gt(self, node):
        node.mongo = "$gt"

    def visit_Lt(self, node):
        node.mongo = "$lt"

    def visit_Add(self, node):
        node.mongo = "$add"

    def visit_Sub(self, node):
        node.mongo = "$subtract"

    def visit_Div(self, node):
        node.mongo = "$divide"

    def visit_Mult(self, node):
        node.mongo = "$multiply"

    def visit_Mod(self, node):
        node.mongo = "$mod"

    def visit_Num(self, node):
        node.mongo = node.n

    def visit_Str(self, node):
        node.mongo = node.s

    def visit_In(self, node):
        node.mongo = "$in"

    def visit_NotIn(self, node):
        node.mongo = "$nin"

    def visit_And(self, node):
        node.mongo = "$and"

    def visit_Or(self, node):
        node.mongo = "$or"

    def visit_Not(self, node):
        node.mongo = "$not"

    def visit_NotEq(self, node):
        node.mongo = "$ne"

    def visit_Attribute(self, node):
        node.mongo = node.attr

    def visit_Compare(self, node):
        self.generic_visit(node)
        v = {}
        v[node.left.mongo] = {}
        v[node.left.mongo][node.ops[0].mongo] = node.comparators[0].mongo
        node.mongo = json.dumps(v)

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        v = {}
        v[node.op.mongo] = []
        for predicate in node.values:
            if isinstance(predicate, ast.Name):
                continue
            if isinstance(predicate, ast.BoolOp):
                v[node.op.mongo].extend(list(map(lambda p: p.mongo, predicate.values)))
                continue
            v[node.op.mongo].append(predicate.mongo)
        node.mongo = json.dumps(v)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        v = {}
        left = "${0}".format(node.left.mongo) if isinstance(node.left, ast.Attribute) else node.left.mongo
        right = "${0}".format(node.right.mongo) if isinstance(node.right, ast.Attribute) else node.right.mongo
        v[node.op.mongo] = [left, right]
        node.mongo = json.dumps(v)

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        v = {}
        v[node.operand.left.attr] = {}
        v[node.operand.left.attr][node.op.mongo] = {}
        v[node.operand.left.attr][node.op.mongo][node.operand.ops[0].mongo] = node.operand.comparators[0].mongo
        node.mongo = json.dumps(v)
