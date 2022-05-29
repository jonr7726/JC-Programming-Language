from . import ir
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

class Print():
    def __init__(self, builder, module, printf, arguments):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.arguments = arguments

    def eval(self, env):
        values = self.arguments.eval(env)

        if len(values) > 1:
            # Printf normally
            if values[0].type == String.TYPE:
                self.builder.call(self.printf, values)
            else:
                raise Exception("Expected first argument of 'print' to be a string literal (found type %s)" %
                    values[0].type)
        else:
            # Print, or printf with single value
            value = values[0]

            if value.type == String.TYPE:
                # Print string directly
                self.builder.call(self.printf, [value])
            else:
                # Format type to string
                if value.type == Character.TYPE:
                    fmt = fmt = "%c\n\0"
                    fmt_name = "fstrc"
                elif value.type == Integer.TYPE:
                    fmt = fmt = "%d\n\0"
                    fmt_name = "fstri"
                elif value.type == Double.TYPE:
                    fmt = fmt = "%f\n\0"
                    fmt_name = "fstrd"
                else:
                    raise Exception("Error type %s invalid for printf" % value.type)

                try:
                    # Get global format string if exists
                    global_fmt = self.module.get_global(fmt_name)
                except KeyError:
                    # Create global format string
                    c_fmt = ir.Constant(ir.ArrayType(Character.TYPE, len(fmt)), bytearray(fmt.encode("utf8")))
                    global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name=fmt_name)
                    global_fmt.linkage = "internal"
                    global_fmt.global_constant = True
                    global_fmt.initializer = c_fmt

                # Declare argument list
                fmt_ptr = self.builder.bitcast(global_fmt, String.TYPE)

                # Call Print Function
                self.builder.call(self.printf, [fmt_ptr, value])