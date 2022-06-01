from ..base import Base

class Continue(Base):
	def eval(self):
		dest = self.state.control.loop_body
		run = self.state.control.loop_incrementor

		if dest != None:
			if run != None:
				run.eval()
			self.state.builder.branch(dest)
			return "CONTINUE"

		raise Exception("Error, cannot continue outside of loop")

class Break(Base):
	def eval(self):
		dest = self.state.control.end

		if dest != None:
			self.state.builder.branch(dest)
			return "BREAK"

		raise Exception("Error, cannot break outside of loop or switch")