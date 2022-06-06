from .base import Base
from llvmlite import ir
from .types import INTEGER_TYPE
from .operations.casting import Cast

def get_array_type(type, size):
    return ir.ArrayType(type, int(size))

class Declaration(Base):
    def __init__(self, state, type, name):
        super().__init__(state)
        self.type = type
        self.name = name
        self.var = Variable(state, name, [], False)

    def eval(self):
        if isinstance(self.type, ir.VoidType):
            raise Exception("Cannot declare variable as type void")

        self.state.variables[self.name] = self.state.builder.alloca(self.type, name=self.name)
        return self.var.eval()

class Assignment(Base):
    def __init__(self, state, var, expression):
        super().__init__(state)
        self.var = var
        self.expression = expression

    def eval(self):
        self.var.load = False

        var = self.var.eval()

        # Cast expression to type of variable
        exp = Cast(self.state, self.expression, var.type.pointee).eval()

        return self.state.builder.store(exp, var)
            
class Variable(Base):
    def __init__(self, state, name, indexs, load):
        super().__init__(state)
        self.name = name
        self.indexs = indexs
        self.load = load

    def derefrence_at(self, index):
        self.indexs.insert(0, index)

    def eval(self):
        # Find var in variables
        var = self._get_var()

        # Derefrence variable at indexs
        if len(self.indexs) != 0:

            if isinstance(var.type.pointee, ir.PointerType):
                # Load first to derefrence initial variable pointer
                var = self.state.builder.load(var)
                indexs = []
            else:
                # (First derefrence is to access array at pointer to variable)
                indexs = [ir.Constant(ir.IntType(64), 0)]

            var = self._get_pointer(var)

            # Evaluate indexs
            for index in self.indexs:
                if index == None:
                    # (For pointer derefrence)
                    indexs.append(ir.Constant(ir.IntType(64), 0))
                else:
                    indexs.append(index.eval())

            # Derefrence at indexs
            var = self.state.builder.gep(var, indexs, inbounds=True)

        else:
            var = self._get_pointer(var)

        if self.load:
            # Load variable
            var = self.state.builder.load(var)

        return var

    def copy(self):
        return Variable(self.state, self.name, self.indexs, self.load)

    def _get_var(self):
        if self.state.variables.get(self.name, False):
            return self.state.variables[self.name]
        else:
            raise Exception("Variable %s not declared" % self.name)

    @staticmethod
    def _get_pointer(var):
        return ir.Constant(var.type, var.get_reference())