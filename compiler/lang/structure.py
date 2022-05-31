from . import Base
from abc import abstractmethod
from llvmlite import ir

class Sequence(Base):
	def __init__(self, state, statement):
		super().__init__(state, type=None)
		self.statements = [statement]

	def add_statement(self, statement):
		self.statements.insert(0, statement)

	def eval(self):
		[statement.eval() for statement in self.statements]

class IfThen(Base):
	def __init__(self, state, condition, then):
		super().__init__(state, type=None)
		self.condition = condition
		self.then = then

	def eval(self):
		with self.state.builder.if_then(self.condition.eval()) as then:
		    self.then.eval()

class IfElse(Base):
	def __init__(self, state, condition, then, otherwise):
		super().__init__(state, type=None)
		self.condition = condition
		self.then = then
		self.otherwise = otherwise

	def eval(self):
		with self.state.builder.if_else(self.condition.eval()) as (then, otherwise):
		    with then:
		    	self.then.eval()
		    with otherwise:
		    	self.otherwise.eval()

class Loop(Base):
	def __init__(self, state, condition, block):
		super().__init__(state, type=None)
		# Loop blocks
		self.condition = condition
		self.block = block
		# Loop jumps
		self.loop_head = None
		self.loop_body = None
		self.loop_end = None

	def eval(self):
		# Create jumps
		self.loop_head = self.state.builder.append_basic_block()
		self.loop_body = self.state.builder.append_basic_block()
		self.loop_end = self.state.builder.append_basic_block()
		
		# Loop start code
		self.start()

		# Loop head code
		self.state.builder.position_at_end(self.loop_head)
		self.head()

		# Loop body code
		self.state.builder.position_at_end(self.loop_body)
		self.body()

		# Loop end code
		self.state.builder.position_at_end(self.loop_end)

	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def head(self):
		pass

	@abstractmethod
	def body(self):
		pass

class PreTest(Loop):
	def start(self):
		# goto head
		self.state.builder.branch(self.loop_head)

	def head(self):
		# If condition, goto body, else go to end
		self.state.builder.cbranch(self.condition.eval(), self.loop_body, self.loop_end)

	def body(self):
		# Run block, then goto head
		self.block.eval()
		self.state.builder.branch(self.loop_head)

class PostWhile(Loop):
	def start(self):
		# goto body
		self.state.builder.branch(self.loop_body)

	def body(self):
		# Run block, then goto head
		self.block.eval()
		self.state.builder.branch(self.loop_head)

	def head(self):
		# If condition, goto body, else go to end
		self.state.builder.cbranch(self.condition.eval(), self.loop_body, self.loop_end)

class PostUntil(Loop):
	def start(self):
		# goto body
		self.state.builder.branch(self.loop_body)

	def body(self):
		# Run block, then goto head
		self.block.eval()
		self.state.builder.branch(self.loop_head)

	def head(self):
		# If condition, goto end, else go to body
		self.state.builder.cbranch(self.condition.eval(), self.loop_end, self.loop_body)


class ForLoop(Loop):
	def __init__(self, state, initializer, condition, itterator, block):
		super().__init__(state, condition, block)
		# Extra loop blocks
		self.initializer = initializer
		self.itterator = itterator

	def start(self):
		# Initialize, then goto head
		self.initializer.eval()
		self.state.builder.branch(self.loop_head)

	def head(self):
		# If condition, goto body, else go to end
		self.state.builder.cbranch(self.condition.eval(), self.loop_body, self.loop_end)

	def body(self):
		# Run block, run itterator, then goto head
		self.block.eval()
		self.itterator.eval()
		self.state.builder.branch(self.loop_head)