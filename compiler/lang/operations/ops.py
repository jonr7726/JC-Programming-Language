from ..base import Base, COMPARISONS
from llvmlite import ir
from .unary_ops import *
from .binary_ops import *
from .logic_gates import *

# Operation class that should be used by parser;
# will handle choosing operation to perform
class Operation(Base): # (Note not Sided, as only its op needs to have that information)
	def __init__(self, state, op_token, left=None, right=None):
		super().__init__(state)

		# (If this fails then parser incorrectly used this library)
		assert(left != None or right != None)

		self.op = self._get_op(op_token, left, right)

	def _get_op(self, op, left, right):
		token = op.gettokentype()

		# Unary operations
		if left == None:
			if token == "-":
				# Negate
				return Negate(self.state, right)
			elif token == "NOT":
				# Boolean NOT
				return BoolNOT(self.state, left, right)
			elif token == "~":
				# Bitwise NOT (ones complement)
				return BitNot(self.state, right)
			else:
				op_str = "%s<expr>" % op.getstr()

		elif right == None:
			op_str = "<expr>%s" % op.getstr()

		# Binary operations
		else:
			# Comparisions
			if token in COMPARISONS:
				return Comparison(self.state, left, right)

			# Arithmetic
			elif token in ("+", "+=", "++"):
				# Addition (signed)
				return Addition(self.state, left, right)
			elif token in ("-", "-=", "--"):
				# Subtraction
				return Subtraction(self.state, left, right)
			elif token in ("*", "*="):
				# Multiplication
				return Multiplication(self.state, left, right)
			elif token in ("/", "/="):
				# Division
				return Division(self.state, left, right)
			elif token in ("PERCENTAGE", "%="):
				# Modulus
				return Modulus(self.state, left, right)

			# Bit shifts
			elif token in ("<<", "<<="):
				# Left shift
				return LeftShift(self.state, left, right)
			elif token in (">>", ">>="):
				# Right shift (signed)
				return RightShift(self.state, left, right)

			# Boolean logic
			elif token == "AND":
				# Boolean AND
				return BoolAND(self.state, left, right)
			elif token == "XOR":
				# Boolean XOR
				return BoolXOR(self.state, left, right)
			elif token == "OR":
				# Boolean OR
				return BoolOR(self.state, left, right)
			elif token == "NAND":
				# Boolean NAND
				return BoolNAND(self.state, left, right)
			elif token == "XNOR":
				# Boolean XNOR
				return BoolXNOR(self.state, left, right)
			elif token == "NOR":
				# Boolean NOR
				return BoolNOR(self.state, left, right)

			# Bitwise logic
			elif token in ("&", "&="):
				# Bitwise AND
				return BitAND(self.state, left, right)
			elif token in ("^", "^="):
				# Bitwise XOR
				return BitXOR(self.state, left, right)
			elif token in ("|", "|="):
				# Bitwise OR
				return BitOR(self.state, left, right)

			else:
				op_str = "<expr> %s <expr>" % op.getstr()

		raise Exception("Invalid operation %s" % op_str)

	def eval(self):
		val = self.op.eval()
		self.type = self.op.type
		return val
