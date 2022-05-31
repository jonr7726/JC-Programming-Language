from llvmlite import ir
from .literals import Integer, Double, String

def get_array_type(type, size):
    return ir.ArrayType(type, int(size))

class Declaration():
    def __init__(self, builder, module, type, name):
        self.builder = builder
        self.module = module
        self.type = type
        self.name = name

    def eval(self, env):
        env.variables[self.name] = self.builder.alloca(self.type, name=self.name)

class Variable():
    def __init__(self, builder, module, name, indexs):
        self.builder = builder
        self.module = module
        self.name = name
        self.indexs = indexs

    def derefrence_at(self, index):
        self.indexs.insert(0, index)

    def get_var(self, env):
        if not env.variables.get(self.name, None) is None:
            return env.variables[self.name]
        else:
            raise Exception("Variable %s not declared" % self.name)

    def get_type(self, env):
        var = self.get_var(env)
        type = var.type.pointee

        # Calculate type if derefrenced
        for index in self.indexs:
            if isinstance(type, ir.ArrayType):
                # (Array)
                type = type.element
            elif isinstance(type, ir.PointerType):
                # (Pointer)
                type = type.pointee
            else:
                raise Exception("Cannot derefrence type %s" % type)

        return type

    def get_pointer(self, env):
        var = self.get_var(env)
        pointer = ir.Constant(var.type, var.get_reference())

        # Derefrence variable at indexs
        if len(self.indexs) != 0:
            # Evaluate indexs
            indexs = [ir.Constant(Integer.TYPE, 0)] # (must be done as variable is pointer already)
            for index in self.indexs:
                indexs.append(index.eval(env))

            # Derefrence at indexs
            pointer = self.builder.gep(pointer, indexs, inbounds=True)

            # Convert back to a pointer (get refrence to output of derefrence)
            pointer = ir.Constant(pointer.type, pointer.get_reference())

        return pointer

    def eval(self, env):
        # Get variable
        return self.builder.load(self.get_pointer(env))