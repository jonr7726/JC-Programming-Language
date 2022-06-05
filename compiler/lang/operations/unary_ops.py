from ..base import Base, FLOATING_TYPES
from abc import abstractmethod
from llvmlite import ir

# Superclass for unary operations
# Will implicity cast both sides to required type, if specified as type argument
# Subclasses should implement eval_op method to perform specific operation
class UnaryOp(Base):
	def __init__(self, state, expression, type=None, signed=None):
		super().__init__(state, type)
		self.expression = expression
		self.signed = signed # (None defaults to signed)

	@abstractmethod
	def eval_op(self, exp_val):
		pass

	def eval(self):
		if self.type != None:
			# Cast to required type before evaluating
			exp_val = Cast(self.state, self.expression, self.type).eval()
		else:
			exp_val = self.expression.eval()

		# Calculate and return operataion result
		return self.eval_op(exp_val)

class Negate(UnaryOp):
	def eval_op(self, exp_val):
		if isinstance(exp_val.type, ir.IntType):
			# Negation of integer
			self.type = exp_val.type
			return self.state.builder.neg(exp_val)
		elif isinstance(exp_val.type, FLOATING_TYPES):
			# Negation of floating point
			self.type = exp_val.type
			return self.state.builder.fneg(exp_val)
		
		raise Exception("Error cannot negate type %s" % exp_val.type)

class Derefrence(UnaryOp):
	"""
	def eval(self, env):
		if isinstance(self.expression, Variable):
			return self.state.builder.bitcast(
				self.expression.get_pointer(env), self.get_type(env))
		else:
			raise Exception("TODO implement this properly")

	def get_type(self, env):
		type = self.expression.get_type(env)
		if isinstance(type, ir.ArrayType):
			# (Array)
			return type.element.as_pointer()
		elif isinstance(type, ir.PointerType):
			# (Pointer)
			return type.pointee.as_pointer()
	"""