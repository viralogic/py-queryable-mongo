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

    def visit(self):
        """
        Pops the first Instruction on the stack and performs visit as given by the op_name
        """
        instruction = self.stack.pop()
        if instruction is None:
            return self.syntax_tree
        visit_method = getattr(self, "visit_{0}".format(instruction.op_name), None)
        if visit_method is None:
            raise AttributeError("Cannot find method visit_{0}".format(instruction.op_name))
        return self.visit_method(instruction)

    def visit_RETURN_VALUE(self, i):
        """
        Performs visit operation on a RETURN_VALUE instruction
        param i: an instance of an instruction
        """
        return ast.Return(self.visit())

    def visit_COMPARE_OP(self, i):
        
