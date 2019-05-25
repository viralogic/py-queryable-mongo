from py_linq_mongo.expressions import LambdaExpression
from unittest import TestCase
import ast


class TestCollectionLambdaTranslator(TestCase):
    """
    Test the methods in the TestCollectionLambdaTranslator class
    """
    def test_Eq(self):
        t = LambdaExpression.parse(lambda x: x.first_name == 'Bruce')
        print(ast.dump(t))
        self.assertIsInstance(t.body.value.ops[0], ast.Eq)
        self.assertEqual("$eq", t.body.value.ops[0].mongo)

    def test_LtE(self):
        t = LambdaExpression.parse(lambda x: x.gpa <= 10)
        self.assertIsInstance(t.body.value.ops[0], ast.LtE)
        self.assertEqual("$lte", t.body.value.ops[0].mongo)

    def test_Lt(self):
        t = LambdaExpression.parse(lambda x: x.gpa < 10)
        self.assertIsInstance(t.body.value.ops[0], ast.Lt)
        self.assertEqual(t.body.value.ops[0].mongo, "$lt")

    def test_GtE(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10)
        self.assertIsInstance(t.body.value.ops[0], ast.GtE)
        self.assertEqual(t.body.value.ops[0].mongo, "$gte")

    def test_Gt(self):
        t = LambdaExpression.parse(lambda x: x.gpa > 10)
        self.assertIsInstance(t.body.value.ops[0], ast.Gt)
        self.assertEqual(t.body.value.ops[0].mongo, "$gt")

    def test_In(self):
        t = LambdaExpression.parse(lambda x: x.first_name in "Bruce")
        self.assertIsInstance(t.body.value.ops[0], ast.In)
        self.assertEqual(t.body.value.ops[0].mongo, "$in")

    def test_NotIn(self):
        t = LambdaExpression.parse(lambda x: x.last_name not in "Fenske")
        self.assertIsInstance(t.body.value.ops[0], ast.NotIn)
        self.assertEqual(t.body.value.ops[0].mongo, "$nin")

    def test_plus(self):
        t = LambdaExpression.parse(lambda x: x.gpa + 10)
        self.assertIsInstance(t.body.value.op, ast.Add)
        self.assertEqual(t.body.value.op.mongo, "$add")

    def test_minus(self):
        t = LambdaExpression.parse(lambda x: x.gpa - 10)
        self.assertIsInstance(t.body.value.op, ast.Sub)
        self.assertEqual(t.body.value.op.mongo, "$subtract")

    def test_div(self):
        t = LambdaExpression.parse(lambda x: x.gpa / 10)
        self.assertIsInstance(t.body.value.op, ast.Div)
        self.assertEqual(t.body.op.mongo, "$divide")

    def test_mult(self):
        t = LambdaExpression.parse(lambda x: x.gpa * 10)
        self.assertIsInstance(t.body.value.op, ast.Mult)
        self.assertEqual(t.body.op.mongo, "$multiply")

    def test_mod(self):
        t = LambdaExpression.parse(lambda x: x.gpa % 2)
        self.assertIsInstance(t.body.value.op, ast.Mod)
        self.assertEqual(t.body.value.op.mongo, "$mod")

    def test_num_binop(self):
        t = LambdaExpression.parse(lambda x: x.gpa * 10)
        self.assertIsInstance(t.body.right, ast.Num, "Should be a Num instance")
        self.assertEqual(t.body.right.mongo, t.body.right.n)

    # def test_return(self):
    #     t = LambdaExpression.translate(lambda x: (x.gpa > 10 and x.first_name == u'Bruce') or x.first_name == u'Dustin')
    #     self.assertEquals(
    #         t.body.sql,
    #         u"(x.gpa > 10 AND x.first_name = 'Bruce') OR x.first_name = 'Dustin'"
    #     )

    def test_num_compare(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10)
        self.assertIsInstance(t.body.comparators[0], ast.Num)
        self.assertEqual(t.body.comparators[0].mongo, t.body.comparators[0].n)

    def test_str(self):
        t = LambdaExpression.parse(lambda x: x.first_name == 'Bruce')
        self.assertIsInstance(t.body.comparators[0], ast.Str)
        self.assertEqual(t.body.comparators[0].mongo, t.body.comparators[0].s)

    def test_attribute(self):
        t = LambdaExpression.parse(lambda x: x.first_name == "Bruce")
        self.assertIsInstance(t.body.left, ast.Attribute)
        self.assertEqual("first_name", t.body.left.mongo)

        t = LambdaExpression.parse(lambda s: s)
        self.assertIsInstance(t.body.id, str)
        self.assertEqual("s", t.body.id)

    def test_and(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10 and x.gpa <= 50)
        self.assertIsInstance(t.body.op, ast.And)
        self.assertEqual(t.body.op.mongo, "$and")

    def test_or(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10 or x.first_name == u'Bruce')
        self.assertIsInstance(t.body.op, ast.Or)
        self.assertEqual(t.body.op.mongo, "$or")

    def test_compare_simple(self):
        t = LambdaExpression.parse(lambda x: x.gpa <= 10)
        self.assertIsInstance(t.body.value, ast.Compare)
        self.assertEqual('{"gpa": {"$lte": 10}}', t.body.value.mongo)

    def test_boolop(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10 and x.gpa <= 50)
        self.assertIsInstance(t.body.value, ast.BoolOp)
        self.assertEqual('{"$and": ["{\\"gpa\\": {\\"$gte\\": 10}}", "{\\"gpa\\": {\\"$lte\\": 50}}"]}', t.body.value.mongo)

    def test_boolop_complex(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10 and x.gpa <= 50 and x.last_name == "Fenske")
        self.assertIsInstance(t.body.value, ast.BoolOp)
        self.assertEqual('{"$and": ["{\\"gpa\\": {\\"$gte\\": 10}}", "{\\"gpa\\": {\\"$lte\\": 50}}", "{\\"last_name\\": {\\"$eq\\": \\"Fenske\\"}}"]}', t.body.mongo)

    def test_boolop_or(self):
        t = LambdaExpression.parse(lambda x: x.gpa >= 10 or x.gpa <= 50 or x.last_name == "Fenske")
        self.assertIsInstance(t.body.value, ast.BoolOp)
        self.assertEqual('{"$or": ["{\\"gpa\\": {\\"$gte\\": 10}}", "{\\"gpa\\": {\\"$lte\\": 50}}", "{\\"last_name\\": {\\"$eq\\": \\"Fenske\\"}}"]}', t.body.value.mongo)

    def test_binop(self):
        t = LambdaExpression.parse(lambda x: x.gpa + 10)
        self.assertIsInstance(t.body.value, ast.BinOp)
        self.assertEqual('{"$add": ["$gpa", 10]}', t.body.mongo)

    def test_not(self):
        t = LambdaExpression.parse(lambda x: not x.gpa == 10)
        self.assertIsInstance(t.body.op, ast.Not)
        self.assertEqual('{"gpa": {"$not": {"$eq": 10}}}', t.body.mongo)

    def test_not_equals(self):
        t = LambdaExpression.parse(lambda x: x.gpa != 10)
        self.assertIsInstance(t.body.ops[0], ast.NotEq)
        self.assertEqual('{"gpa": {"$ne": 10}}', t.body.mongo)

    # def test_unary(self):
    #     t = SqlLambdaTranslatorTest.translate(self.simple_not)
    #     correct = u"NOT x.gpa = 10"
    #     self.assertEqual(
    #         t.body.sql,
    #         correct,
    #         u"{0} sql property should equal {1}".format(t.body.sql, correct)
    #     )

    # def test_Lambda(self):
    #     t = SqlLambdaTranslatorTest.translate(self.simple_and)
    #     correct = u"x.gpa >= 10 AND x.gpa <= 50"
    #     self.assertEqual(t.body.sql, correct,
    #                      u"{0} should equal {1}".format(t.body.sql, correct))

    # def test_simple_select(self):
    #     t = SqlLambdaTranslatorTest.translate(self.simple_select)
    #     self.assertEqual(t.body.sql, u"x.first_name", u"Should equal 'x.first_name")

    # def test_order_by(self):
    #     t = SqlLambdaTranslatorTest.translate(self.simple_order_by)
    #     self.assertEqual(t.body.sql, u"x.first_name", u"Should equal 'x.first_name'")

    # def test_list_select(self):
    #     t = SqlLambdaTranslatorTest.translate(self.list_select)
    #     correct = u"x.first_name, x.last_name, x.gpa"
    #     self.assertEqual(
    #         t.body.sql,
    #         correct,
    #         u"{0} should equal {1}".format(t.body.sql, correct)
    #     )

    # def test_tuple_select(self):
    #     t = SqlLambdaTranslatorTest.translate(self.tuple_select)
    #     correct = u"x.first_name, x.last_name, x.gpa"
    #     self.assertEqual(
    #         t.body.sql,
    #         correct,
    #         u"{0} should equal {1}".format(t.body.sql, correct)
    #     )

    # def test_dict_select(self):
    #     t = SqlLambdaTranslatorTest.translate(self.dict_select)
    #     correct = u"x.first_name AS 'FirstName', x.last_name AS 'LastName', x.gpa AS 'GPA'"
    #     self.assertEqual(
    #         t.body.sql,
    #         correct,
    #         u"{0} should equal {1}".format(t.body.sql, correct)
    #     )
