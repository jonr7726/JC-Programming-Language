from ..base import Base

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
			if evals[-1] in ("BREAK", "CONTINUE", "RETURN"):
				# Do not run code after interupter statements
				break
				
		return evals