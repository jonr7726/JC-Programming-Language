from . import ir
from .variables import Declaration, Variable
from .literals import Integer, Double
from .unops import IntegerCast, DoubleCast

class BinaryOp():
	def __init__(self, builder, module, left, right):
		self.builder = builder
		self.module = module
		self.left = left
		self.right = right

	def is_doubles(self, env):
		return (self.left.get_type(env) == Double.TYPE and self.right.get_type(env) == Double.TYPE)

	def is_ints(self, env):
		return (self.left.get_type(env) == Integer.TYPE and self.right.get_type(env) == Integer.TYPE)

	def is_int_double(self, env):
		return (Double.TYPE in [self.left.get_type(env), self.right.get_type(env)] and
			Integer.TYPE in [self.left.get_type(env), self.right.get_type(env)])

	def to_double(self, env):
		if self.left.get_type(env) == Integer.TYPE:
			return self.builder.sitofp(self.left.eval(env), Double.TYPE), self.right.eval(env)
		else:
			return self.left.eval(env), self.builder.sitofp(self.right.eval(env), Double.TYPE)

	def get_type(self, env):
		if self.left.get_type(env) == self.right.get_type(env):
			return self.left.get_type(env)
		elif self.is_int_double(env):
			return Double.TYPE
		else:
			return [self.left.get_type(env), self.right.get_type(env)]


class Addition(BinaryOp):
	def eval(self, env):
		if self.is_ints(env):
			return self.builder.add(self.left.eval(env), self.right.eval(env))
		elif self.is_doubles(env):
			return self.builder.fadd(self.left.eval(env), self.right.eval(env))
		elif self.is_int_double(env):
			lhs, rhs = self.to_double(env)
			return self.builder.fadd(lhs, rhs)
		else:
			raise Exception("Cannot perform addition on types %s and %s" % (self.left.get_type(env), self.right.get_type(env)))


class Subtraction(BinaryOp):
	def eval(self, env):
		if self.is_ints(env):
			return self.builder.sub(self.left.eval(env), self.right.eval(env))
		elif self.is_doubles(env):
			return self.builder.fsub(self.left.eval(env), self.right.eval(env))
		elif self.is_int_double(env):
			lhs, rhs = self.to_double(env)
			return self.builder.fsub(lhs, rhs)
		else:
			raise Exception("Cannot perform subtraction on types %s and %s" % (self.left.get_type(env), self.right.get_type(env)))

class Multiplication(BinaryOp):
	def eval(self, env):
		if self.is_ints(env):
			return self.builder.mul(self.left.eval(env), self.right.eval(env))
		elif self.is_doubles(env):
			return self.builder.fmul(self.left.eval(env), self.right.eval(env))
		elif self.is_int_double(env):
			lhs, rhs = self.to_double(env)
			return self.builder.fmul(lhs, rhs)
		else:
			raise Exception("Cannot perform multiplication on types %s and %s" % (self.left.get_type(env), self.right.get_type(env)))

class Division(BinaryOp):
	def eval(self, env):
		if self.is_ints(env):
			return self.builder.sdiv(self.left.eval(env), self.right.eval(env))
		elif self.is_doubles(env):
			return self.builder.fdiv(self.left.eval(env), self.right.eval(env))
		elif self.is_int_double(env):
			lhs, rhs = self.to_double(env)
			return self.builder.fdiv(lhs, rhs)
		else:
			raise Exception("Cannot perform division on types %s and %s" % (self.left.get_type(env), self.right.get_type(env)))

class Assignment(BinaryOp):
	def eval(self, env):
		if isinstance(self.left, Declaration):
			self.left.eval(env)
			self.left = Variable(self.builder, self.module, self.left.name)

		if self.left.get_type(env) == self.right.get_type(env):
			self.builder.store(self.right.eval(env), self.left.get_pointer(env))
		elif self.left.get_type(env) == Double.TYPE and self.right.get_type(env) == Integer.TYPE:
			# Can't use is_doubles as this only works if assigning to a double
			self.builder.store(self.builder.sitofp(self.right.eval(env), Double.TYPE), self.left.get_pointer(env))
		else:
			raise Exception("Cannot perform assignment an %s and %s" % (self.left.get_type(env), self.right.get_type(env)))
