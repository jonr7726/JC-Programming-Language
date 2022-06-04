from ..base import Base, FLOATING_TYPES
from abc import abstractmethod
from llvmlite import ir
from .unary_ops import Cast

# Attempts to cast the right side and left side so they are of the same type
# Cast will attempt to avoid loss of data when choosing which side's type to cast to
# If no transformation can be made results in an error
class ImplicitCast(Cast):
	def __init__(self, state, left, right):
		super().__init__(state, None, None)
		self.left = left
		self.right = right

	def eval(self):
		# Evaluate both sides
		left_val = self.left.eval()
		right_val = self.right.eval()

		# Find appropriate cast to avoid data loss
		if isinstance(left_val.type, type(right_val.type)):
			# Already the same
			if isinstance(left_val.type, ir.IntType):
				# Resize integer
				if left_val.type.width > right_val.type.width:
					self.type = left_val.type
				else:
					self.type = right_val.type
			else:
				# No casting necessary
				return left_val, right_val

		elif isinstance(left_val.type, ir.PointerType):
			if isinstance(right_val.type, ir.IntType):
				# Cast pointer to integer
				self.type = right_val.type

		elif isinstance(left_val.type, ir.IntType):
			if isinstance(right_val.type, FLOATING_TYPES):
				# Cast integer to floating point
				self.type = right_val.type

		elif isinstance(left_val.type, FLOATING_TYPES):
			if isinstance(right_val.type, ir.IntType):
				# Cast integer to floating point
				self.type = left_val.type

			elif isinstance(right_val.type, FLOATING_TYPES):
				# Resize floating point (to larger precision)
				if isinstance(left_val, ir.HalfType) or (
					isinstance(left_val, ir.FloatType) and isinstance(right_val, ir.DoubleType)):

					# (Right value larger)
					self.type = right_val.type
				else:
					self.type = left_val.type

		if self.type != None:
			return self.eval_op(left_val), self.eval_op(right_val)
		else:
			raise Exception("Cannot implicitly cast types %s and %s" % (
				left_val.type, right_val.type))


# Superclass for binary operations
# Will implicity cast both sides to same time avoiding data loss
# or to required type, if specified as type argument
# Subclasses should implement eval_op method to perform specific operation
class BinaryOp(Base):
	def __init__(self, state, left, right, type=None, op=None, signed=None):
		super().__init__(state, type=type)
		self.left = left
		self.right = right
		self.op = op
		self.signed = signed # (None defaults to signed)

	@abstractmethod
	def eval_op(self, left_val, right_val):
		pass

	def eval(self):
		if self.type != None:
			# Implicity cast left and right sides to required type
			left_val = Cast(self.state, self.left, self.type).eval()
			right_val = Cast(self.state, self.right, self.type).eval()
		else:
			# Implicitly cast left and right sides and set the type
			cast = ImplicitCast(self.state, self.left, self.right)
			left_val, right_val = cast.eval()
			self.type = cast.type

		# Calculate and return operataion result
		return self.eval_op(left_val, right_val)

class Addition(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer addition
			return self.state.builder.add(left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point addition
			return self.state.builder.fadd(left_val, right_val)

		raise Exception("Cannot perform addition on types %s and %s" % (
			left_val.type, right_val.type))

class Subtraction(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer subtraction
			return self.state.builder.sub(left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point subtraction
			return self.state.builder.fsub(left_val, right_val)

		raise Exception("Cannot perform subtraction on types %s and %s" % (
			left_val.type, right_val.type))

class Multiplication(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer multiplication
			return self.state.builder.mul(left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point multiplication
			return self.state.builder.fmul(left_val, right_val)

		raise Exception("Cannot perform multiplication on types %s and %s" % (
			left_val.type, right_val.type))

class Division(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			if self.signed == False:
				# Integer division (un-signed)
				return self.state.builder.udiv(left_val, right_val)
			else:
				# Integer division (signed)
				return self.state.builder.sdiv(left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point division
			return self.state.builder.fdiv(left_val, right_val)

		raise Exception("Cannot perform division on types %s and %s" % (
			left_val.type, right_val.type))

class Modulus(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			if self.signed == False:
				# Integer modulus (un-signed)
				return self.state.builder.urem(left_val, right_val)
			else:
				# Integer modulus (signed)
				return self.state.builder.srem(left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point modulus
			return self.state.builder.frem(left_val, right_val)

		raise Exception("Cannot perform Remainder on types %s and %s" % (
			left_val.type, right_val.type))

class LeftShift(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			# Integer left shift
			return self.state.builder.shl(left_val, right_val)

		raise Exception("Cannot left shift type %s by type %s" % (
			left_val.type, right_val.type))

class RightShift(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			if self.signed == False:
				# Integer right shift (un-signed; arithmetical)
				return self.state.builder.lshr(left_val, right_val)
			else:
				# Integer right shift (signed; logical)
				return self.state.builder.ashr(left_val, right_val)

		raise Exception("Cannot right shift type %s by type %s" % (
			left_val.type, right_val.type))

class Comparison(BinaryOp):
	def eval_op(self, left_val, right_val):
		if isinstance(self.type, ir.IntType):
			if self.signsigned == False:
				# Integer comparison (un-signed)
				return self.state.builder.icmp_unsigned(self.op, left_val, right_val)
			else:
				# Integer comparison (signed)
				return self.state.builder.icmp_signed(self.op, left_val, right_val)
		elif isinstance(self.type, FLOATING_TYPES):
			# Floating point comparison (ordered; QNAN values are not allowed -if one side is QNAN, then always returns false)
			# TODO implement relevent fast math flags
			return self.state.builder.fcmp_ordered(self.op, left_val, right_val)

		raise Exception("Cannot perform comparison on types %s and %s" % (
			left_val.type, right_val.type))
