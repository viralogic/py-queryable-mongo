import dis
import ast
from ..data_structures import Stack


class InstructionVisitor(object):
    """
    Performs operations on a set of instructions
    """
    def __init__(self, instructions):
        """
        Default constructor
        :param instructions: an iterable of instruction objects
        """
        self.stack = Stack()
        for i in instructions:
            if not isinstance(i, dis.Instruction):
                raise TypeError("instruction is not an instance of dis.Instruction")
            self.stack.push(i)

    def visit(self, i=None):
        """
        Pops the first Instruction on the stack and performs visit as given by the op_name
        """
        instruction = self.stack.pop() if i is None else i
        if instruction is None:
            return
        visit_method = getattr(self, "visit_{0}".format(instruction.opname), None)
        if visit_method is None:
            raise AttributeError("Cannot find method visit_{0}".format(instruction.op_name))
        return visit_method(instruction)

    def visit_RETURN_VALUE(self, i):
        """
        Performs visit operation on a RETURN_VALUE instruction
        param i: an instance of an instruction
        """
        # return ast.Return(self.visit(i))
        raise NotImplementedError()

    def visit_COMPARE_OP(self, i):
        """
        Performs visit operation on a COMPARE_OP instruction
        param i: an instance of an instruction
        """
        op_map = {
            '>=': ast.GtE,
            '<=': ast.LtE,
            '>': ast.Gt,
            '<': ast.Lt,
            '==': ast.Eq,
            '!=': ast.NotEq,
            'in': ast.In,
            'not in': ast.NotIn,
            'is': ast.Is,
            'is not': ast.IsNot
        }
        right = self.stack.pop()
        left = self.stack.pop()
        return ast.Compare(
            left=self.visit(left),
            ops=[op_map[i.argval]()],
            comparators=[self.visit(right)],
            lineno=i.starts_line,
            col_offset=i.offset
        )

    def __determine_const(self, argval, lineno, offset):
        if isinstance(argval, str):
            return ast.Str(s=argval, lineno=lineno, col_offset=offset, is_jump_target=False)
        if isinstance(argval, (int, float, complex)):
            return ast.Num(n=argval, lineno=lineno, col_offset=offset, is_jump_target=False)
        if isinstance(argval, tuple):
            elts = []
            for item in i.argval:
                node = self.__determine_const(item)
                node.lineno = lineno
                node.col_offset = offset
                node.is_jump_target = False
                elts.append(node)
            return ast.Tuple(elts=elts, ctx=ast.Load(), lineno=lineno, col_offset=offset, is_jump_target=False)
        if i.argval is None:
            return ast.Name(id='None', ctx=_ast.Load(), lineno=lineno, col_offset=offset, is_jump_target=False)
        return arg

    def visit_LOAD_CONST(self, i):
        """
        Performs visit operation on LOAD_CONST instruction
        :param i: an Instruction instance
        """
        node = self.__determine_const(i.argval, i.starts_line, i.offset)
        node.lineno = i.starts_line
        node.col_offset = 0
        node.is_jump_target = False
        return node
