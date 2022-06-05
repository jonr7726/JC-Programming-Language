from .base import Base
from llvmlite import ir
from .types import *

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
	def __init__(self, state, value):
		super().__init__(state, int(value), INTEGER_TYPE)

class Long(Literal):
	def __init__(self, state, value):
		super().__init__(state, int(value), LONG_TYPE)

class Double(Literal):
	def __init__(self, state, value):
		super().__init__(state, float(value), DOUBLE_TYPE)

class Boolean(Literal):
	def __init__(self, state, value):
		super().__init__(state, (1 if str(value) == "true" else 0),
			BOOLEAN_TYPE)

class Character(Literal):
	def __init__(self, state, value):
		super().__init__(state, sanatize_char(value), CHARACTER_TYPE)

class String(Literal):
	def __init__(self, state, value):
		super().__init__(state, sanatize_string(value),
			CHARACTER_TYPE.as_pointer())

	def eval(self):
		# Make constant character array
		value = ir.Constant(ir.ArrayType(self.type.pointee, len(self.value)),
			self.value)

		# Check if string literal already exists
		for var in self.state.module.global_values:
			if isinstance(var, ir.GlobalVariable):
				if var.initializer == value:
					return self.state.builder.bitcast(var, self.type)

		# Make global variable of string literal
		literal = ir.GlobalVariable(self.state.module, value.type,
			name=self.state.module.get_unique_name("str"))
		literal.linkage = "private"
		literal.global_constant = True
		literal.unnamed_addr = True
		literal.initializer = value

		# Convert pointer to character array to character pointer
		return self.state.builder.bitcast(literal, self.type)
		#return self.state.builder.gep(literal, , inbounds=True)