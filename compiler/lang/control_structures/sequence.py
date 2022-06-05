from ..base import Base
from .interupter import Break, Continue, Return

class Sequence(Base):
	def __init__(self, state, statement):
		super().__init__(state, type=None)
		self.statements = [statement]

	def add_statement(self, statement):
		self.statements.insert(0, statement)
		return self

	def eval(self):
		evals = []
		for statement in self.statements:
			evals.append(statement.eval())
			if isinstance(evals[-1], (Break, Continue, Return)):
				# Do not run code after interupter statements (unreachable)
				break
				
		return evals