from . import ir
from .literals import Integer, Double

class Variable():
    def __init__(self, builder, module, name):
        self.builder = builder
        self.module = module
        self.name = name

    def get_var(self, env):
        if not env.variables.get(self.name, None) is None:
            return env.variables[self.name]
        else:
            raise Exception("Variable %s not declared" % self.name)

    def get_type(self, env):
        var = self.get_var(env)
        return var.type.pointee

    def get_pointer(self, env):
        var = self.get_var(env)
        return ir.Constant(var.type, var.get_reference())

    def eval(self, env):
        return self.builder.load(self.get_pointer(env))

class Declaration():
    def __init__(self, builder, module, type, name):
        self.builder = builder
        self.module = module
        self.type = type
        self.name = name

    def eval(self, env):
        if self.type == "INT":
            type = Integer.TYPE
        elif self.type == "DOUBLE":
            type = Double.TYPE
        else:
            raise TypeError("Invalid type %s" % self.type)

        env.variables[self.name] = self.builder.alloca(type, name=self.name)