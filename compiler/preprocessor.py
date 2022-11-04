import re
import os

def remove_comments(text):
	# Removes all comments from file
	single_line = r"\/\/.*\n"
	multi_line = r"\/\*(?:(?!\*\/)[\s\S])*\*\/"
	text = re.sub(single_line, "\n", text)
	text = re.sub(multi_line, "", text)

	return text

def next_include(text):
	# Find all include statements from text
	return re.search(r"(?:\n|^)include[\ \t]+\"((?:(?!\")[\s\S])*)\"", text)

class Preprocessor():
	def __init__(self, directory):
		self.directory = directory

	def process(self, text):
		# Remove comments
		text = remove_comments(text)
		# Find next include statement
		include = next_include(text)

		while include is not None:
			# Get file path
			path = os.path.join(self.directory, include.groups()[0])

			# Get contents from included file
			try:
				file = open(path)
				include_text = file.read()
				file.close()
			except FileNotFoundError:
				raise Exception("Error, file at %r does not exist" % path)

			# Run pre-processor on included file
			include_text = this.process(include_text)

			# Insert file contexts into include line
			text = (text[:include.span()[0]] +
				"\n" + include_text +
				text[include.span()[1]:])

		return text