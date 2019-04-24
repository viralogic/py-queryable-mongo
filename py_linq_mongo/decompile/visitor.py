import dis
import ast
from ..data_structures import Stack, Queue


class InstructionVisitor(object):
    """
    Performs operations on a set of instructions
    """
    def __init__(self, instructions=[], stack=None):
        """
        Default constructor
        :param instructions: an iterable of instruction objects
        """
        if stack is not None:
            self.stack = stack
        else:
            branch_pts = ['JUMP_IF_FALSE_OR_POP', 'JUMP_IF_TRUE_OR_POP']
            if_pts = ['POP_JUMP_IF_FALSE']
            self.stack = Stack()
            instructions = list(instructions)
            idx = 0
            while idx < len(instructions):
                i = instructions[idx]
                if not isinstance(i, dis.Instruction):
                    raise TypeError("instruction is not an instance of dis.Instruction")
                if i.opname == "RETURN_VALUE":
                    idx += 1
                    continue
                if i.opname in branch_pts:
                    visitor = InstructionVisitor(stack=self.stack.copy())
                    self.stack = Queue()
                    self.stack.push(i)
                    self.stack.push(visitor)
                    instructions = list(reversed(instructions[idx + 1:]))
                    idx = 0
                    continue
                if i.opname in if_pts:
                    visitor = InstructionVisitor(stack=self.stack.copy())
                    self.stack = Queue()
                    self.stack.push(i)
                    self.stack.push(visitor)
                    instructions = instructions[idx + 1:]
                    idx = 0
                    continue
                self.stack.push(i)
                idx += 1

    def visit(self, i=None):
        """
        Pops the first Instruction on the stack and performs visit as given by the op_name
        """
        self.stack = Stack(self.stack.items)
        instruction = self.stack.pop() if i is None else i
        if instruction is None:
            return None
        visit_method = getattr(self, "visit_{0}".format(instruction.opname), None)
        if visit_method is None:
            raise AttributeError("Cannot find method visit_{0}".format(instruction.op_name))
        return visit_method(instruction)

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
            return ast.Str(s=argval, lineno=lineno, col_offset=offset)
        if isinstance(argval, (int, float, complex)):
            return ast.Num(n=argval, lineno=lineno, col_offset=offset)
        if isinstance(argval, tuple):
            elts = []
            for item in i.argval:
                node = self.__determine_const(item)
                node.lineno = lineno
                node.col_offset = offset
                elts.append(node)
            return ast.Tuple(elts=elts, ctx=ast.Load(), lineno=lineno, col_offset=offset)
        if i.argval is None:
            return ast.Name(id='None', ctx=ast.Load(), lineno=lineno, col_offset=offset)
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

    def visit_LOAD_FAST(self, i):
        """
        Performs visit operation on LOAD_FAST instruction
        :param i: an Instruction instance
        """
        return ast.Name(
            id=i.argval,
            ctx=ast.Load(),
            lineno=i.starts_line,
            col_offset=i.offset
        )

    def visit_LOAD_ATTR(self, i):
        """
        Performs visit operation on LOAD_ATTR instruction
        :param i: an Instruction instance
        """
        name_instruction = self.stack.pop()
        return ast.Attribute(
            value=self.visit(name_instruction),
            attr=i.argval,
            ctx=ast.Load(),
            lineno=i.starts_line,
            col_offset=i.offset
        )

    def visit_JUMP_IF_FALSE_OR_POP(self, i):
        left_ast = self.stack.pop().visit()
        right_instruction = self.stack.pop()
        return ast.BoolOp(
            op=ast.And(),
            values=[left_ast, self.visit(right_instruction)]
        )

    def visit_JUMP_IF_TRUE_OR_POP(self, i):
        left_ast = self.stack.pop().visit()
        right_instruction = self.stack.pop()
        return ast.BoolOp(
            op=ast.Or(),
            values=[left_ast, self.visit(right_instruction)]
        )

    def visit_POP_JUMP_IF_FALSE(self, i):
        left_ast = self.stack.pop().visit()
        body_instruction = self.stack.pop()
        right_instruction = self.stack.pop()
        return ast.IfExp(
            test=left_ast,
            body=self.visit(body_instruction),
            orelse=self.visit(right_instruction)
        )
