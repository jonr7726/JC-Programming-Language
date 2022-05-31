from . import Base
from llvmlite import ir
from .literals import Integer, Double, Character, String

class Arguments(Base):
    def __init__(self, state, argument):
        super().__init__(state)
        self.arguments = [argument]
    
    def add_argument(self, argument):
        self.arguments.insert(0, argument)
        
    def eval(self):
        args = [arg.eval() for arg in self.arguments]
        self.type = [arg.type for arg in args]
        return args

class Function(Base):
    def __init__(self, state, function, arguments):
        super().__init__(state)
        self.arguments = arguments
        self.function = self.functions[function]
        self.type = self.function.return_value.type

    def eval(self):
        args = self.arguments.eval()
        return self.builder.call(self.function, self.args.eval())