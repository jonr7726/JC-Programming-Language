from .unary_ops import *
from .binary_ops import *

# (Ones complement)
class BitNOT(UnaryOp):
	def eval_op(self, exp_val):
		if isinstance(exp_val.type, ir.IntType):
			# Negation of integer
			self.type = exp_val.type
			return self.state.builder.not_(exp_val)

		raise Exception("Error cannot perform bitwise NOT on type %s"
			% exp_val.type)

class BoolNOT(BitNOT):
	def __init__(self, state, expression):
		# Convert expression to boolean before performing bitwise NOT
		super().__init__(state, expression, type=ir.IntType(1), signed=False)

class BitAND(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer bitwise AND
			return self.state.builder.and_(left_val, right_val)

		raise Exception("Cannot perform bitwise AND on types %s and %s" % (
			left_val.type, right_val.type))

class BoolAND(BitAND):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise AND
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)

class BitOR(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer bitwise OR
			return self.state.builder.or_(left_val, right_val)

		raise Exception("Cannot perform bitwise OR on types %s and %s" % (
			left_val.type, right_val.type))

class BoolOR(BitOR):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise OR
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)

class BitXOR(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer bitwise XOR
			return self.state.builder.xor(left_val, right_val)

		raise Exception("Cannot perform bitwise XOR on types %s and %s" % (
			left_val.type, right_val.type))

class BoolXOR(BitXOR):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise XOR
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)

class BitNAND(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Perform bitwise NOT on output of bitwise AND
			return self.state.builder.not_(
				self.state.builder.and_(
					left_val, right_val))
		
		raise Exception("Cannot perform bitwise NAND on types %s and %s" % (
			left_val.type, right_val.type))

class BoolNAND(BitNAND):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise NAND
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)

class BitXNOR(BitXOR):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Perform bitwise NOT on output of bitwise XOR
			return self.state.builder.not_(
				self.state.builder.xor(
					left_val, right_val))
		
		raise Exception("Cannot perform bitwise XNOR on types %s and %s" % (
			left_val.type, right_val.type))

class BoolXNOR(BitXNOR):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise XNOR
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)

class BitNOR(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Perform bitwise NOT on output of bitwise OR
			return self.state.builder.not_(
				self.state.builder.or_(
					left_val, right_val))
		
		raise Exception("Cannot perform bitwise NOR on types %s and %s" % (
			left_val.type, right_val.type))

class BoolNOR(BitNOR):
	def __init__(self, state, left, right):
		# Convert expression to boolean before performing bitwise NOR
		super().__init__(state, left, right, type=ir.IntType(1), signed=False)