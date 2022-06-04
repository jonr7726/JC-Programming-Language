from ..base import Base, FLOATING_TYPES
from abc import abstractmethod
from llvmlite import ir

# Casts expression to another type (if not already the same)
class Cast(Base):
	def __init__(self, state, expression, type, signed=None):
		super().__init__(state, type)
		self.expression = expression
		self.signed = signed # (None defaults to signed)

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