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

    def eval(self):
        self.variables[self.name] = self.builder.alloca(self.type, name=self.name)

class Assignment(Base):
    def __init__(self, state, var, expression):
        super().__init__(state)
        self.var = var
        self.expression = expression

    def eval(self):
        if isinstance(self.var, Declaration):
            self.var.eval()
            self.var = Variable(self.builder, self.module, self.var.name)

        var, exp = self._implicit_cast(self.var.eval(), self.expression.eval())

        if var.type.pointee == exp.type:
            return self.builder.store(exp, var)

        raise Exception("Cannot assign type %s to type %s" % (exp.type, var.type))

    @staticmethod
    def _implicit_cast(var, exp):
        if isinstance(var.type.pointee, ir.FloatType) and isinstance(exp.type, ir.IntType):
            # Cast to double
            exp = Cast(exp, var.type.pointee)

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
        if self.load:
            # Get variable from pointer
            return self.builder.load(self._get_pointer())
        else:
            # Get variable pointer
            return self._get_pointer()

    def _get_var(self):
        if self.variables.get(self.name, False):
            return self.variables[self.name]
        else:
            raise Exception("Variable %s not declared" % self.name)

    def _get_pointer(self):
        var = self._get_var()
        pointer = ir.Constant(var.type, var.get_reference())

        # Derefrence variable at indexs
        if len(self.indexs) != 0:
            # Evaluate indexs
            indexs = [ir.Constant(Integer.TYPE, 0)] # (Add 0 as variable itself is a pointer)
            for index in self.indexs:
                indexs.append(index.eval())

            # Derefrence at indexs
            pointer = self.builder.gep(pointer, indexs, inbounds=True)

            # Convert back to a pointer (get refrence to output of derefrence)
            #pointer = ir.Constant(pointer.type, pointer.get_reference())

        return pointer