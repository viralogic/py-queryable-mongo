from unittest import TestCase
import dis
import ast
from py_linq_mongo.decompile.visitor import InstructionVisitor


class InstructionVisitorTest(TestCase):

    def test_Compare(self):
        instruction = dis.Instruction(
            opname='COMPARE_OP',
            opcode=107,
            arg=2,
            argval='==',
            argrepr='==',
            offset=6,
            starts_line=None,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Compare)
        self.assertIsInstance(t.ops[0], ast.Eq)

    def test_Constant_Str(self):
        instruction = dis.Instruction(
            opname='LOAD_CONST',
            opcode=100,
            arg=1,
            argval='Western Hockey League',
            argrepr="'Western Hockey League'",
            offset=4,
            starts_line=None,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Str)
        self.assertIsInstance(t.s, str)
        self.assertEqual(t.s, 'Western Hockey League')

    def test_Constant_Num(self):
        instruction = dis.Instruction(
            opname='LOAD_CONST',
            opcode=100,
            arg=1,
            argval=99,
            argrepr="99",
            offset=4,
            starts_line=None,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Num)
        self.assertIsInstance(t.n, int)
        self.assertEqual(t.n, 99)

    def test_Attribute(self):
        instruction = dis.Instruction(
            opname='LOAD_ATTR',
            opcode=106,
            arg=0,
            argval='name',
            argrepr='name',
            offset=2,
            starts_line=None,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Attribute)
        self.assertIsNone(t.value)
        self.assertEqual('name', t.attr)

    def test_Load_Fast(self):
        instruction = dis.Instruction(
            opname='LOAD_FAST',
            opcode=124,
            arg=0,
            argval='x',
            argrepr='x',
            offset=0,
            starts_line=1,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Name)
        self.assertEqual('x', t.id)

    def test_Return_Value(self):
        instruction = dis.Instruction(
            opname='RETURN_VALUE',
            opcode=83,
            arg=None,
            argval=None,
            argrepr='',
            offset=8,
            starts_line=None,
            is_jump_target=False
        )
        visitor = InstructionVisitor([instruction])
        t = visitor.visit()
        self.assertIsInstance(t, ast.Return)
        self.assertIsNone(t.value)

    def test_simple_lambda(self):
        instructions = dis.get_instructions(lambda x: x.name == "Western Hockey League")
        visitor = InstructionVisitor(instructions)
        t = visitor.visit()
        self.assertIsInstance(t, ast.Return)
        self.assertIsInstance(t.value, ast.Compare)
        self.assertIsInstance(t.value.left, ast.Attribute)
        self.assertEqual(1, len(t.value.comparators))
        self.assertIsInstance(t.value.comparators[0], ast.Str)
        self.assertIsInstance(t.value.left.value, ast.Name)
