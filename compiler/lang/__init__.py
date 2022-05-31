from rply.token import BaseBox
from abc import abstractmethod

class Base(BaseBox):
	def __init__(self, state, type=None):
		self.state = state
		self.type = type

	@abstractmethod
	def eval():
		pass
		# After eval run, self.type must be initialized