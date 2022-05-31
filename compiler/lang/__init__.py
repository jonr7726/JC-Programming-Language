from rply.token import BaseBox
from abc import abstractmethod

class Base(BaseBox):
	def __init__(self, state, type=None):
		self.builder = state.builder
		self.module = state.module
		self.functions = state.functions
		self.variables = state.variables

	@abstractmethod
	def eval():
		pass
		# After eval run, self.type must be initialized