from ast import NodeVisitor
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


class CollectionLambdaTranslator(NodeVisitor):
    """
    Visitor for converting lambda expressions into Mongo query
    """
    def __init__(self):
        """
        Default constructor
        :param collection_type: The Model type
        """
        super(CollectionLambdaTranslator, self).__init__()

    def visit_Eq(self, node):
        node.mongo = "$eq"

    def visit_LtE(self, node):
        node.mongo = u"$lte"

    def visit_GtE(self, node):
        node.mongo = u"$gte"

    def visit_Gt(self, node):
        node.mongo = u"$gt"

    def visit_Lt(self, node):
        node.mongo = u"$lt"

    def visit_Add(self, node):
        node.mongo = u"$add"

    def visit_Sub(self, node):
        node.mongo = u"$subtract"

    def visit_Div(self, node):
        node.mongo = u"$divide"

    def visit_Mult(self, node):
        node.mongo = u"$multiply"

    def visit_Mod(self, node):
        node.mongo = u"$mod"

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
        node.mongo = u"$ne"
