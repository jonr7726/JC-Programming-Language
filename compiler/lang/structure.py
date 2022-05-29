from . import ir

class Program():
	def __init__(self, builder, module, statement):
		self.builder = builder
		self.module = module
		self.statements = [statement]

	def add_statement(self, statement):
		self.statements.insert(0, statement)

	def eval(self, env):
		result = None

		for statement in self.statements:
			result = statement.eval(env)

		return result