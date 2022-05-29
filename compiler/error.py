class Error():
	def __init__(self, message):
		message = message[0].upper() + message[1:] # (As first letter in message must be uppercase)
		print("ERROR: " + message)
		quit()