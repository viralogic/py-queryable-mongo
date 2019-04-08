import abc
import dis


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
        return self.generate_ast(instructions)

    @abc.abstractmethod
    def _generate_ast(self, instructions):
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

    def decompile(self, instructions):
        """
        Decompiles a lambda expression into an abstract syntax tree
        :param instructions: an iterable of instructions
        :returns: an abstract syntax tree
        """
        raise NotImplementedError()
