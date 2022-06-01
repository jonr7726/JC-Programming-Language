from ..base import Base
from abc import abstractmethod

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
		# Create block jumps
		self.loop_head = self.state.builder.append_basic_block()
		self.loop_body = self.state.builder.append_basic_block()
		self.loop_end = self.state.builder.append_basic_block()

		# Set loop body and end for break / continues
		self.state.control.loop_body = self.loop_head
		self.state.control.end = self.loop_end
		
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
		self.end()

		# Reset block jump locations (for continue and break statements)
		self.state.control.loop_body = None
		self.state.control.end = None

	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def head(self):
		pass

	@abstractmethod
	def body(self):
		pass

	@abstractmethod
	def end(self):
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
	def __init__(self, state, initializer, condition, incrementor, block):
		super().__init__(state, condition, block)
		# Extra loop blocks
		self.initializer = initializer
		self.incrementor = incrementor

	def start(self):
		# Set iterator (for continues)
		self.state.control.loop_incrementor = self.incrementor

		# Initialize, then goto head
		self.initializer.eval()
		self.state.builder.branch(self.loop_head)

	def head(self):
		# If condition, goto body, else go to end
		self.state.builder.cbranch(self.condition.eval(), self.loop_body, self.loop_end)

	def body(self):
		# Run block, run incrementor, then goto head
		self.block.eval()
		self.incrementor.eval()
		self.state.builder.branch(self.loop_head)

	def end(self):
		# Reset iterator (for continues)
		self.state.control.loop_incrementor = None