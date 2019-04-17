import abc
import dis
import ast
from .visitor import InstructionVisitor


class Decompiler(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    def decompile(self, code):
        """
        Decompiles a code object into an AST
        :param code: a code object
        :returns: an abstract syntax tree
        """
        instructions = dis.get_instructions(code)
        return self._generate_ast(code, instructions)

    @abc.abstractmethod
    def _generate_ast(self, code, instructions):
        """
        Converts a set of instructions to an abstract syntax tree
        :param instructions: an iterable of instructions
        :returns: an abstract syntax tree
        """
        raise NotImplementedError()


class LambdaDecompiler(Decompiler):
    """
    Class used to decompile a lambda code object to an abstract syntax tree
    """
    def __init__(self):
        super(LambdaDecompiler, self).__init__()

    def _generate_ast(self, code, instructions):
        """
        Decompiles a lambda expression into an abstract syntax tree
        :param instructions: an iterable of instructions
        :returns: an abstract syntax tree
        """
        instructions = list(instructions)
        visitor = InstructionVisitor(instructions)
        lineno = instructions[0].starts_line if instructions is not None and len(instructions) > 0 else 0
        body = ast.Return(
            value=visitor.visit(),
            lineno=lineno,
            col_offset=0
        )
        args = [ast.Name(id=arg, ctx=ast.Param()) for arg in code.co_varnames[:code.co_argcount]]
        co_locals = code.co_varnames[code.co_argcount:]
        return ast.Lambda(
            args=ast.arguments(
                args=args,
                defaults=[],
                vararg=co_locals.pop(0) if code.co_flags & 4 else None,
                kwarg=co_locals.pop() if code.co_flags & 8 else None,
                lineno=lineno,
                col_offset=0
            ),
            body=body,
            lineno=lineno,
            col_offset=0
        )
