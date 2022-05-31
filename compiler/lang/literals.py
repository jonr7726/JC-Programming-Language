from . import Base
from llvmlite import ir

def sanatize(string):
	character_map = {
		"\\\\": "\\",
		"\\n" : "\n",
		"\\r" : "\r",
		"\\t" : "\t",
		"\\b" : "\b",
		"\\f" : "\f",
		"\\'" : "\'",
		"\\0" : "\0",
	}

	# Remove quotation marks
	string = string[1:-1]

	# Map characters
	for char in character_map:
		string = string.replace(char, character_map[char])

	# Convert to byte array
	return bytearray(string.encode("utf8"))

def sanatize_char(char):
	char = sanatize(char)
	if len(char) == 1:
		return char[0]
	else:
		raise Exception("Char cannot be more than 1 character long :", char)

def sanatize_string(string):
	# Add string terminator
	string = string[:-1] + "\0" + string[-1]

	return sanatize(string)

class Literal(Base):
	def __init__(self, state, value, type):
		super().__init__(state, type=type)
		self.value = value

	def eval(self):
		return ir.Constant(self.type, self.value)

class Integer(Literal):
    TYPE = ir.IntType(32)

    def __init__(self, state, value):
        super().__init__(state, int(value), self.TYPE)

class Double(Literal):
    TYPE = ir.DoubleType()

    def __init__(self, state, value):
        super().__init__(state, float(value), self.TYPE)

class Boolean(Literal):
	TYPE = ir.IntType(1)

	def __init__(self, state, value):
		super().__init__(state, (1 if str(value) == "true" else 0), self.TYPE)

class Character(Literal):
	TYPE = ir.IntType(8)

	def __init__(self, state, value):
		super().__init__(state, sanatize_char(value), self.TYPE)

class String(Literal):
	TYPE = Character.TYPE.as_pointer()

	def __init__(self, state, value):
		super().__init__(state, sanatize_string(value), self.TYPE)

	def eval(self):
		# Make constant character array
		value = ir.Constant(ir.ArrayType(Character.TYPE, len(self.value)), self.value)

		# Check if string literal already exists
		for var in self.state.module.global_values:
			if isinstance(var, ir.GlobalVariable):
				if var.initializer == value:
					return self.state.builder.bitcast(var, String.TYPE)

		# Make global variable of string literal
		literal = ir.GlobalVariable(self.state.module, value.type, name=self.state.module.get_unique_name("str"))
		literal.linkage = "private"
		literal.global_constant = True
		literal.unnamed_addr = True
		literal.initializer = value

		# Convert pointer to character array to character pointer
		return self.state.builder.bitcast(literal, String.TYPE)
		#return self.state.builder.gep(literal, , inbounds=True)