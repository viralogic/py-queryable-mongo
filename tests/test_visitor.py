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
