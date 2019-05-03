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

    def __determine_const(self, i):
        if isinstance(i.argval, str):
            return ast.Str(s=i.argval, lineno=i.starts_line, col_offset=i.offset, is_jump_target=False)
        if isinstance(i.argval, (int, float, complex)):
            return ast.Num(n=i.argval, lineno=i.starts_line, col_offset=i.offset, is_jump_target=False)
        if isinstance(i.argval, tuple):
            args = []
            for item in i.argval:
                args.append(self.__determine_const(dis.Instruction(
                    opname=i.opname,
                    opcode=i.opcode,
                    arg=i.arg,
                    argval=item,
                    argrepr=item.__repr__(),
                    offset=i.offset,
                    starts_line=i.starts_line,
                    is_jump_target=i.is_jump_target
                )))
            return args
        if i.argval is None:
            return ast.Name(id='None', ctx=ast.Load(), lineno=i.starts_line, col_offset=i.offset, is_jump_target=False)
        return i.argval

    def visit_LOAD_CONST(self, i):
        """
        Performs visit operation on LOAD_CONST instruction
        :param i: an Instruction instance
        """
        return self.__determine_const(i)

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

    def visit_LOAD_GLOBAL(self, i):
        return ast.Name(
            id=i.argval,
            ctx=ast.Load(),
            lineno=i.starts_line,
            col_offset=i.offset
        )

    def visit_BUILD_TUPLE(self, i):
        nodes = []
        while self.stack.top() is not None:
            node = self.stack.pop()
            nodes.append(self.visit(node))
        return ast.Tuple(
            elts=list(reversed(nodes)),
            ctx=ast.Load()
        )

    def visit_BUILD_LIST(self, i):
        nodes = []
        while self.stack.top() is not None:
            node = self.stack.pop()
            nodes.append(self.visit(node))
        return ast.List(
            elts=list(reversed(nodes)),
            ctx=ast.Load()
        )

    def visit_BUILD_CONST_KEY_MAP(self, i):
        keys = self.stack.pop()
        num_keys = len(keys.argval)
        keys_attr = self.visit(keys)
        nodes = []
        j = 0
        while j < num_keys:
            node = self.stack.pop()
            nodes.append(self.visit(node))
            j += 1
        return ast.Dict(
            keys=keys_attr,
            values=list(reversed(nodes)),
            ctx=ast.Load()
        )


