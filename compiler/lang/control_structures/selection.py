from ..base import Base
from .interupter import Break, Continue, Return

class BinarySelection(Base):
	def __init__(self, state, condition, then, otherwise=None):
		super().__init__(state, type=None)
		self.condition = condition
		self.then = then
		self.otherwise = otherwise

	def eval(self):
		# Create block jumps
		if isinstance(self.then.statements[0], Break):
			# Optimisation by using condition branch for 'if (condition) {break;}'
			then = self.state.control.end
		else:
			then = self.state.builder.append_basic_block()
		if self.otherwise == None:
			# If selection has no otherwise (else),
			# then set the end to the otherwise block
			otherwise = self.state.builder.append_basic_block()
			endif = otherwise
		else:
			endif = self.state.builder.append_basic_block()
			if isinstance(self.otherwise.statements[0], Break):
				# (Optimisation mentioned above)
				otherwise = self.state.control.end
			else:
				otherwise = self.state.builder.append_basic_block()

		# Create binary branch
		self.state.builder.cbranch(self.condition.eval(), then, otherwise)

		# Create then block
		if not isinstance(self.then.statements[0], Break):
			self.state.builder.position_at_end(then)
			self.then.eval()
			if not isinstance(self.then.statements[-1], (Break, Continue, Return)):
				self.state.builder.branch(endif)

		# Create otherwise (else) block
		if self.otherwise != None:
			if not isinstance(self.otherwise.statements[0], Break):
				self.state.builder.position_at_end(otherwise)
				self.otherwise.eval()
				if not isinstance(self.otherwise.statements[-1], (Break, Continue, Return)):
					self.state.builder.branch(endif)
		
		self.state.builder.position_at_end(endif)

class MultiwaySelection(Base):
	def __init__(self, state, block):
		super().__init__(state, type=None)
		self.default = block
		self.values = []
		self.blocks = []

		self.expression = None

	def add_case(self, value, block):
		self.values.insert(0, value)
		self.blocks.insert(0, block)
		return self

	def set_expression(self, expression):
		self.expression = expression
		return self

	def eval(self):
		def make_block(block, case, broken):
			# Goto next block
			if not broken:
				self.state.builder.branch(case)
			self.state.builder.position_at_end(case)

			# Create code in block
			block_val = block.eval()[-1]

			if isinstance(block_val, Continue):
				raise Exception("Error, cannot continue inside a switch statement")

			# Return if broken
			return isinstance(block_val, (Break, Return))

		# Create block jumps
		start = self.state.builder.block
		cases = [self.state.builder.append_basic_block() for block in self.blocks]
		default = self.state.builder.append_basic_block() if self.default != None else None
		end = self.state.builder.append_basic_block()

		# Set end point for break statements
		self.state.control.end = end

		broken = False
		for block, case in zip(self.blocks, cases):
			broken = make_block(block, case, broken)

		# Add default case
		if default != None:
			broken = make_block(self.default, default, broken)

		# Return to main control sequence
		if not broken:
			self.state.builder.branch(end)

		# Create switch
		self.state.builder.position_at_end(start)
		switch = self.state.builder.switch(self.expression.eval(), default)

		# Add cases to switch statement
		for value, case in zip(self.values, cases):
			switch.add_case(value.eval(), case)

		self.state.builder.position_at_end(exit)