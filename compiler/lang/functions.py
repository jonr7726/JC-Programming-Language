from .base import Base
from llvmlite import ir
from .operations.casting import Cast
from .variables import Declaration, Assignment
from .control_structures.interupter import Return

class CallArgs(Base):
    def __init__(self, state, arg=None):
        super().__init__(state)
        self.args = []
        if arg != None:
            self.add_arg(arg)
    
    def add_arg(self, arg):
        self.args.insert(0, arg)
        
    def eval(self):
        args = [arg.eval() for arg in self.args]
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

class FunctionArgs(Base):
    def __init__(self, state, arg_type=None, arg_name=None):
        super().__init__(state)
        self.names = []
        self.type = []
        if arg_type != None:
            self.add_arg(arg_type, arg_name)
    
    def add_arg(self, arg_type, arg_name):
        self.names.append(arg_name.getstr())
        self.type.append(arg_type)
        
    def eval(self):
        return self.type

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

            # Allocate function arguments as variables
            # (and reset scope of other local variables)
            self.state.variables = {}
            for name, arg in zip(self.args.names,
                self.state.builder.function.args):

                var = Declaration(self.state, arg.type, name).eval()
                self.state.builder.store(arg, var)

            # Evaluate function block content
            block = self.block.eval()

            # Add return statement for void functions
            if not isinstance(block[-1], Return) and (
                isinstance(self.return_type, ir.VoidType)):

                block.append(Return(self.state).eval())

            elif not isinstance(block[-1], Return) and (
                not isinstance(self.return_type, ir.VoidType)):

                raise Exception("Must return value from non-void function")

        return block