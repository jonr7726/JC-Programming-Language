from . import Base
from llvmlite import ir

class Program(Base):
	def __init__(self, state, statement):
		super().__init__(state, type=None)
		self.statements = [statement]

	def add_statement(self, statement):
		self.statements.insert(0, statement)

	def eval(self):
		return [statement.eval() for statement in self.statements]