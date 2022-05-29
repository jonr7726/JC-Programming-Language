from . import ir

def sanatize_string(string):
	character_map = {
		"\\\\": "\\",
		"\\n" : "\n",
		"\\r" : "\r",
		"\\t" : "\t",
		"\\b" : "\b",
		"\\f" : "\f",
		"\\'" : "\'",
	}

	# Remove quotation marks
	string = string[1:-1] + "\0"

	# Map characters
	for char in character_map:
		string = string.replace(char, character_map[char])

	# Convert to byte array
	return bytearray(string.encode("utf8"))

class Literal():
    def __init__(self, builder, module, value, type):
        self.builder = builder
        self.module = module
        self.value = value
        self.type = type

    def get_type(self, env):
        return self.type

    def eval(self, env):
        return ir.Constant(self.type, self.value)

class Integer(Literal):
    TYPE = ir.IntType(32)

    def __init__(self, builder, module, value):
        super().__init__(builder, module, int(value), self.TYPE)

class Double(Literal):
    TYPE = ir.DoubleType()

    def __init__(self, builder, module, value):
        super().__init__(builder, module, float(value), self.TYPE)

class Character(Literal):
	TYPE = ir.IntType(8)

	def __init__(self, builder, module, value):
		super().__init__(builder, module, sanatize_string(value), self.TYPE)

class String(Literal):
	TYPE = Character.TYPE.as_pointer()

	def __init__(self, builder, module, value):
		super().__init__(builder, module, sanatize_string(value), self.TYPE)

	def eval(self, env):
		# Make constant character array
		value = ir.Constant(ir.ArrayType(ir.IntType(8), len(self.value)), self.value)

		# Make global variable of string literal
		global_fmt = ir.GlobalVariable(self.module, value.type, name=self.module.get_unique_name("string"))
		global_fmt.linkage = "internal"
		global_fmt.global_constant = True
		global_fmt.initializer = value

		# Bitcast character array to character pointer
		return self.builder.bitcast(global_fmt, String.TYPE)