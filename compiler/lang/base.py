from rply.token import BaseBox
from abc import abstractmethod
from llvmlite import ir

# Constants
FLOATING_TYPES = (ir.HalfType, ir.FloatType, ir.DoubleType)
COMPARISONS = ("==", "!=", "<=", ">=", "<", ">")

# Base language super class
class Base(BaseBox):
	def __init__(self, state, type=None):
		self.state = state
		self.type = type

	# After eval run, self.type must be initialized
	@abstractmethod
	def eval():
		pass

# (Does nothing)
class Pass(Base):
	def __init__(self):
		super().__init__(None, type=None)

	def eval():
		pass