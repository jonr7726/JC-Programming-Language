from . import ir
from .literals import Integer, Double

class UnaryOp():
	def __init__(self, builder, module, expression):
		self.builder = builder
		self.module = module
		self.expression = expression

	def get_type(self, env):
		return self.expression.get_type(env)

class IntegerCast(UnaryOp):
	def eval(self, env):
		if self.expression.get_type(env) == Double.TYPE:
			return self.builder.fptosi(self.expression.eval(env), Integer.TYPE)
		else:
			raise Exception("Error cannot convert type %s to integer" % self.expression.get_type(env))

	def get_type(self, env):
		return Integer.TYPE

class DoubleCast(UnaryOp):
	def eval(self, env):
		if self.expression.get_type(env) == Integer.TYPE:
			return self.builder.sitofp(self.expression.eval(env), Double.TYPE)
		else:
			raise Exception("Error cannot convert type %s to double" % self.expression.get_type(env))

	def get_type(self, env):
		return Double.TYPE

class Negative(UnaryOp):
	def eval(self, env):
		if self.expression.get_type(env) in [Integer.TYPE, Double.TYPE]:
			return self.builder.neg(self.expression.eval(env))
		else:
			raise Exception("Error cannot make type %s negative" % self.expression.get_type(env))