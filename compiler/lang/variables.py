from . import Base
from llvmlite import ir
from .literals import Integer, Double, String

def get_array_type(type, size):
    return ir.ArrayType(type, int(size))

class Declaration(Base):
    def __init__(self, state, type, name):
        super().__init__(state)
        self.type = type
        self.name = name
        self.var = Variable(state, name, [], False)

    def eval(self):
        self.state.variables[self.name] = self.state.builder.alloca(self.type, name=self.name)
        return self.var.eval()

class Assignment(Base):
    def __init__(self, state, var, expression):
        super().__init__(state)
        self.var = var
        self.expression = expression

    def eval(self):
        if isinstance(self.var, Variable):
            # (Not declaration; variable must not be loaded)
            self.var.load = False

        var, exp = self._implicit_cast(self.var.eval(), self.expression.eval())

        if var.type.pointee == exp.type:
            return self.state.builder.store(exp, var)
            
        raise Exception("Cannot assign type %s to type %s" % (exp.type, var.type))

    @staticmethod
    def _implicit_cast(var, exp):
        if isinstance(var.type.pointee, ir.FloatType) and isinstance(exp.type, ir.IntType):
            # Cast to double
            exp = Cast(self.state, exp, var.type.pointee)

        return var, exp


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

        # Get register pointer to variable
        var = self._get_pointer(var)

        # Derefrence variable at indexs
        if len(self.indexs) != 0:
            # Load variable
            var = self.state.builder.load(var)

            # Evaluate indexs
            #indexs = [ir.Constant(Integer.TYPE, 0)] # (Add 0 as variable itself is a pointer)
            indexs = []
            for index in self.indexs:
                indexs.append(index.eval())

            # Derefrence at indexs
            var = self.state.builder.gep(var, indexs, inbounds=True)

            # Get register pointer to output of above statement
            var = self._get_pointer(var)

        if self.load:
            # Load variable
            var = self.state.builder.load(var)

        return var

    def _get_var(self):
        if self.state.variables.get(self.name, False):
            return self.state.variables[self.name]
        else:
            raise Exception("Variable %s not declared" % self.name)

    @staticmethod
    def _get_pointer(var):
        return ir.Constant(var.type, var.get_reference())