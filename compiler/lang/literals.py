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
		super().__init__(builder, module, sanatize_char(value), self.TYPE)

class String(Literal):
	TYPE = Character.TYPE.as_pointer()

	def __init__(self, builder, module, value):
		super().__init__(builder, module, sanatize_string(value), self.TYPE)

	def eval(self, env):
		# Make constant character array
		value = ir.Constant(ir.ArrayType(Character.TYPE, len(self.value)), self.value)

		# Make global variable of string literal
		global_fmt = ir.GlobalVariable(self.module, value.type, name=self.module.get_unique_name("string"))
		global_fmt.linkage = "private"
		global_fmt.global_constant = True
		global_fmt.unnamed_addr = True
		global_fmt.initializer = value

		# Convert pointer to character array to character pointer
		return self.builder.bitcast(global_fmt, String.TYPE)
		#return self.builder.gep(global_fmt, , inbounds=True)