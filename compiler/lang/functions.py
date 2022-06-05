from .base import Base
from llvmlite import ir
from .operations.casting import Cast
from .control_structures.interupter import Return

class Arguments(Base):
    def __init__(self, state, argument=None):
        super().__init__(state)
        self.arguments = []
        if argument != None:
            self.add_argument(argument)
    
    def add_argument(self, argument):
        self.arguments.insert(0, argument)
        
    def eval(self):
        args = [arg.eval() for arg in self.arguments]
        self.type = [arg.type for arg in args]
        return args

class Call(Base):
    def __init__(self, state, func, args):
        super().__init__(state)
        self.args = args
        self.func = func

    def eval(self):
        if not self.func in self.state.functions:
            raise Exception("Function '%s' is not defined" % self.func)

        func = self.state.functions[self.func]

        self.type = func.return_value.type

        return self.state.builder.call(func, self.args.eval())

class Function(Base):
    def __init__(self, state, name, return_type, args, block=None):
        super().__init__(state)
        self.name = name.getstr()
        self.return_type = return_type
        self.args = args
        self.block = block # (None for declarations)

        self.func = self.__declare()

    def __declare(self):
        if self.name in self.state.functions:
            raise Exception("Cannot redeclare function %s" % self.name)

        func_type = ir.FunctionType(self.return_type, self.args.eval(), False)
        func = ir.Function(self.state.module, func_type, name=self.name)

        self.state.functions[self.name] = func
        return func

    def eval(self):
        block = None
        if self.block != None:
            # Add function content
            func_block = self.func.append_basic_block(name="entry")
            self.state.builder.position_at_end(func_block)
            block = self.block.eval()

            # Add return statement for void functions
            if not isinstance(block[-1], Return) and (
                isinstance(self.return_type, ir.VoidType)):

                block.append(Return(self.state).eval())

            elif not isinstance(block[-1], Return) and (
                not isinstance(self.return_type, ir.VoidType)):

                raise Exception("Must return value from non-void function")

        return block