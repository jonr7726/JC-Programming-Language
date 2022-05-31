from . import Base
from abc import abstractmethod
from llvmlite import ir
from .variables import Declaration, Variable
from .literals import Integer, Double
from .unops import Cast

class BinaryOp(Base):
	def __init__(self, state, left, right):
		super().__init__(state)
		self.__left = left
		self.__right = right

	@abstractmethod
	def eval_op(self, left_val, right_val):
		pass

	def eval(self):
		left_val, right_val = self._implicit_cast(__left.eval(), __right.eval())
		self._set_type(left_val, right_val)
		return self.eval_op(left_val, right_val)

	@staticmethod
	def _implicit_cast(left_val, right_val):
		if isinstance(left_val.type, ir.IntType) and isinstance(right_val.type, ir.FloatType):
			# Cast left to floating point
			left_val = Cast(left_val, right_val.type).eval()
		elif isinstance(left_val.type, ir.FloatType) and isinstance(right_val.type, ir.IntType):
			# Cast right to floating point
			right_val = Cast(right_val, left_val.type).eval()

		return left_val, right_val

	def _set_type(left_val, right_val):
		if left_val.type == right_val.type:
			self.type = left_val.type
		else:
			self.type = None

class Addition(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer addition
			return self.builder.add(left_val, right_val)
		elif isinstance(self.type, ir.FloatType):
			# Floating point addition
			return self.builder.fadd(left_val, right_val)

		raise Exception("Cannot perform addition on types %s and %s" % (left_val.type, right_val.type))

class Subtraction(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer subtraction
			return self.builder.sub(left_val, right_val)
		elif isinstance(self.type, ir.FloatType):
			# Floating point subtraction
			return self.builder.fsub(left_val, right_val)

		raise Exception("Cannot perform subtraction on types %s and %s" % (left_val.type, right_val.type))

class Multiplication(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer multiplication
			return self.builder.sub(left_val, right_val)
		elif isinstance(self.type, ir.FloatType):
			# Floating point multiplication
			return self.builder.fsub(left_val, right_val)

		raise Exception("Cannot perform multiplication on types %s and %s" % (left_val.type, right_val.type))

class Division(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer division
			return self.builder.sdiv(left_val, right_val)
		elif isinstance(self.type, ir.FloatType):
			# Floating point division
			return self.builder.fdiv(left_val, right_val)

		raise Exception("Cannot perform division on types %s and %s" % (left_val.type, right_val.type))
