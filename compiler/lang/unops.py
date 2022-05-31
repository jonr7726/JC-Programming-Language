from . import Base
from abc import abstractmethod
from llvmlite import ir
from .literals import Integer, Double
from .variables import Variable

class UnaryOp(Base):
	def __init__(self, state, expression, type=None):
		super().__init__(state, type)
		self.__expression = expression

	def eval(self):
		return self.eval_op(self.__expression.eval())

	@abstractmethod
	def eval_op(self, exp_val):
		pass

class Cast(UnaryOp):
	def __init__(self, state, expression, type):
		super().__init__(state, expression, type=type)

	def eval_op(self, exp_val):
		if isinstance(self.type, ir.IntType):
			if isinstance(exp_val.type, ir.FloatType):
				# Floating point to integer
				return self.state.builder.fptosi(exp_val, self.type)

			elif isinstance(exp_val.type, ir.PointerType):
				# Pointer to integer
				return self.state.builder.ptrtoint(exp_val, self.type)

		elif isinstance(self.type, ir.FloatType):
			if isinstance(exp_val.type, ir.IntType):
				# Integer to floating point
				return self.state.builder.sitofp(exp_val, self.type)

		elif isinstance(self.type, ir.PointerType):
			if isinstance(exp_val.type, ir.ArrayType):
				# Array to pointer
				if exp_val.type.element == self.type.pointee:
					return self.state.builder.bitcast(exp_val, self.type)

			elif isinstance(exp_val.type, ir.IntType):
				# Integer to pointer
				return self.state.builder.inttoptr(exp_val, self.type)

		raise Exception("Error cannot cast type %s to type %s " % exp_val.type, self.type)

class Negate(UnaryOp):
	def eval_op(self, exp_val):
		if isinstance(exp_val.type, (ir.IntType, ir.FloatType)):
			self.type = exp_val.type
			return self.state.builder.neg(exp_val)
		
		raise Exception("Error cannot negate type %s" % exp_val.type)

class Derefrence(UnaryOp):
	"""
	def eval(self, env):
		if isinstance(self.expression, Variable):
			return self.state.builder.bitcast(self.expression.get_pointer(env), self.get_type(env))
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