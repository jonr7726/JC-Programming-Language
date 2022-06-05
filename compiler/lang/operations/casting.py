from ..base import Base
from llvmlite import ir

# Casts expression to another type (if not already the same)
class Cast(Base):
	def __init__(self, state, expression, type, signed=None):
		super().__init__(state, type)
		self.expression = expression
		self.signed = signed # (None defaults to signed)

	# (Used by subclasses that override eval)
	def eval_op(self, exp_val):
		if isinstance(self.type, type(exp_val.type)):
			# Already the same
			if isinstance(self.type, ir.IntType):
				# Resize integer
				if self.type.width > exp_val.type.width:
					# Extend size
					if self.signed == False:
						# Extend size (un-signed)
						return self.state.builder.zext(exp_val, self.type)
					else:
						# Extend size (signed)
						return self.state.builder.sext(exp_val, self.type)
				else:
					# Reduce size
					if self.type.width == 1:
						# Convert to boolean (check if value != 0)
						return self.state.builder.icmp_unsigned(
							"!=", exp_val, ir.Constant(ir.IntType(1), 0))
					else:
						# Reduce size
						return self.state.builder.trunc(exp_val, self.type)
			else:
				# No casting necessary
				return exp_val

		elif isinstance(self.type, ir.IntType):
			if isinstance(exp_val.type, FLOATING_TYPES):
				# Floating point to integer
				if self.signed == False:
					# Floating point to integer (unsigned)
					return self.state.builder.fptoui(exp_val, self.type)
				else:
					# Floating point to integer (signed)
					return self.state.builder.fptosi(exp_val, self.type)

			elif isinstance(exp_val.type, ir.PointerType):
				# Pointer to integer
				return self.state.builder.ptrtoint(exp_val, self.type)

		elif isinstance(self.type, FLOATING_TYPES):
			if isinstance(exp_val.type, ir.IntType):
				# Integer to floating point
				if self.signed == False:
					# Integer (un-signed) to floating point
					return self.state.builder.uitofp(exp_val, self.type)
				else:
					# Integer (signed) to floating point
					return self.state.builder.sitofp(exp_val, self.type)

			elif isinstance(exp_val.type, FLOATING_TYPES):
				# Resize floating point
				if isinstance(exp_val.type, ir.HalfType) or (
					isinstance(exp_val.type, ir.FloatType) and isinstance(self.type, ir.DoubleType)):
					
					# Extend size
					return self.state.builder.fpext(exp_val, self.type)
				else:
					# Reduce size
					return self.state.builder.fptrunc(exp_val, self.type)

		elif isinstance(self.type, ir.PointerType):
			if isinstance(exp_val.type, ir.ArrayType):
				# Array to pointer
				if isinstance(exp_val.type.element, self.type.pointee):
					return self.state.builder.bitcast(exp_val, self.type)

			elif isinstance(exp_val.type, ir.IntType):
				# Integer to pointer
				return self.state.builder.inttoptr(exp_val, self.type)

		raise Exception("Error cannot cast type %s to type %s " % (
			exp_val.type, self.type))

	def eval(self):
		# Evaluate expression
		return self.eval_op(self.expression.eval())

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