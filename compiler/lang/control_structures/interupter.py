from ..base import Base
from llvmlite import ir
from ..operations.casting import Cast

class Continue(Base):
	def eval(self):
		dest = self.state.control.loop_body
		run = self.state.control.loop_incrementor

		if dest != None:
			if run != None:
				# Run loop incrementor (for 'for' loops)
				run.eval()
			self.state.builder.branch(dest)
			return self

		raise Exception("Error, cannot continue outside of loop")

class Break(Base):
	def eval(self):
		dest = self.state.control.end

		if dest != None:
			self.state.builder.branch(dest)
			return self

		raise Exception("Error, cannot break outside of loop or switch")

class Return(Base):
	def __init__(self, state, expression=None):
		super().__init__(state)
		self.expression = expression # (None for void returns)

	def eval(self):
		# (Return type of current function)
		self.type = self.state.builder.function.return_value.type

		if isinstance(self.type, ir.VoidType):
			if self.expression == None:
				# Return void
				self.state.builder.ret_void()
				return self
			else:
				raise Exception("Error, cannot return value from void function")

		else:
			if self.expression != None:
				# Implicity cast expression to return type
				expr = Cast(self.state, self.expression, self.type).eval()

				# Return expression
				self.state.builder.ret(expr)
				return self
			else:
				raise Exception("Error, must specify value to return for non-void function")