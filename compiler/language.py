from llvmlite import ir

class Program():
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)
    
    def add_statement(self, statement):
        self.statements.insert(0, statement)
        
    def eval(self, env):
        result = None

        for statement in self.statements:
            result = statement.eval(env)

        return result

class Variable():
    def __init__(self, type, name):
        self.name = name
        self.type = type
        self.value = None

    def get_name(self):
        return str(self.name)

    def eval(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name].eval(env)
            return ir.Constant(ir.IntType(8), int(self.value))
        raise NameError("Not yet defined")

class Integer():
    def __init__(self, builder, module, value):
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self, env):
        return ir.Constant(ir.IntType(8), int(self.value))


class BinaryOp():
    def __init__(self, builder, module, left, right):
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right


class Addition(BinaryOp):
    def eval(self, env):
        i = self.builder.add(self.left.eval(env), self.right.eval(env))
        return i


class Subtraction(BinaryOp):
    def eval(self, env):
        i = self.builder.sub(self.left.eval(env), self.right.eval(env))
        return i

class Assignment(BinaryOp):
    def eval(self, env):
        if env.variables.get(self.left.get_name(), None) is None:
            env.variables[self.left.get_name()] = self.right
            return self.right.eval(env)

class Print():
    def __init__(self, builder, module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self, env):
        value = self.value.eval(env)

        # Declare argument list
        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
        global_fmt.linkage = "internal"
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        # Call Print Function
        self.builder.call(self.printf, [fmt_arg, value])