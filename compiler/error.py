class JCError(Exception):
	def __init__(self, message):
		message = message[0].upper() + message[1:] # (As first letter in message must be uppercase)
		super().__init__("ERROR: " + message)