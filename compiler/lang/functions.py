from llvmlite import ir
from .literals import Integer, Double, Character, String

class Arguments():
    def __init__(self, builder, module, argument):
        self.builder = builder
        self.module = module
        self.arguments = [argument]
    
    def add_argument(self, argument):
        self.arguments.insert(0, argument)
        
    def eval(self, env):
        return [arg.eval(env) for arg in self.arguments]

class Function():
    def __init__(self, builder, module, functions, function, arguments):
        self.builder = builder
        self.module = module
        self.function = functions[function]
        self.arguments = arguments

    def eval(self, env):
        return self.builder.call(self.function, self.arguments.eval(env))

    def get_type(self, env):
        return self.function.return_value.type