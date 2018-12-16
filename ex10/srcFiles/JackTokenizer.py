# ============== Imports ==============
# from .TokenTypes import *
# from .Token import Token
from TokenTypes import *
from Token import Token
import re

# ============= Constants =============

COMMENTS_2_REGEX = r'//.*'
COMMENTS_1_REGEX = r'/\*(\*(?!/)|[^*])*\*/'
NO_TOKENS = 'Called get_current_token function while there are no tokens'
READ_PERMISSIONS = "r"
COMMENT_LINE_1_PREFIX = "//"
COMMENT_LINE_2_PREFIX = "/*"
REGEX_PATTERN = r"[a-zA-Z0-9]+|\".+?\"|\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~|\S+"
INT_REGEX = re.compile(r"^([+-]?[1-9]\d*|0)$")


# ======= Class Implementation =======

class JackTokenizer:
	"""
	This class removes all comments and white spaces from the input stream
	and breaks it into Jack-language tokens, as specified by the Jack grammar.
	"""

	def __init__(self, input_file_path):
		"""
		Opens the input file and copies all non empty and non comments lines to a lines list.
		:param input_file_path: a given ".jack" file.
		This function assumes the input file path is a valid path to a valid file.
		"""
		with open(input_file_path, READ_PERMISSIONS) as input_file:
			# Copy non-empty or comment lines from given file into list
			input_file_lines = []
			for line in input_file:
				# Remove inline comments
				stripped_line = self.__remove_comments(line)
				# If line is empty, continue
				if len(stripped_line) == 0:
					continue
				# If there is an open comment tag without an ending tag
				if stripped_line.find("/*") != -1:
					current_line = stripped_line + " "
					line = next(input_file)
					while line.find("*/") == -1 or line.find("/*") != -1:
						current_line += line + " "
						line = next(input_file)
					current_line += line + " "
					stripped_line = self.__remove_comments(current_line)
					# If line is empty, continue
					if len(stripped_line) == 0:
						continue
				# Add line
				input_file_lines.append(stripped_line)
		# Init variables
		self.__input_file = input_file_lines
		self.__tokens = []
		self.__token_index = 0
		self.__line_index = 0

	def __remove_comments(self, line):
		"""
		Receives a line with possible comments in it,
		and removes all allowed comments in jack language from the line.
		:param line: A line with possible comments in it
		:return: A line with no comments
		"""
		# Remove spaces
		stripped_line = line.strip()
		# Remove // comments if it comes before /* or /** comment
		if stripped_line.find("/*") != -1 and stripped_line.find("//") < stripped_line.find(
				"/*") or stripped_line.find("//") != -1:
			stripped_line = re.sub(COMMENTS_2_REGEX, "", stripped_line)
		# Remove /** and /* comments that end in the same line
		stripped_line = re.sub(COMMENTS_1_REGEX, "", stripped_line)
		return stripped_line

	def __parse_line(self):
		"""
		This function should be called only if all tokens in self.__tokens already been used
		It will clear this list and parse the next line from self.__input_file into that list.
		"""
		tokens = re.findall(REGEX_PATTERN, self.__input_file[self.__line_index])
		self.__tokens.clear()
		for token in tokens:
			if token in keyword_dict:
				current = Token(Type.KEYWORD, token)
			elif token in symbols_dict:
				current = Token(Type.SYMBOL, token)
			elif token.startswith('\"') and token.endswith('\"'):
				token = token[1:-1]
				current = Token(Type.STRING_CONST, token)
			elif INT_REGEX.match(token.strip()) is not None:
				current = Token(Type.INT_CONST, token)
			else:
				current = Token(Type.IDENTIFIER, token)
			self.__tokens.append(current)

	def __update_tokens(self):
		"""
		This function will parse the next line from self.__input_file
		(if there is a line to parse)
		:return: True if there were more tokens to parse, false otherwise
		"""
		if self.__line_index >= len(self.__input_file):
			return False
		self.__token_index = 0
		self.__parse_line()
		self.__line_index += 1
		return True

	def has_more_tokens(self):
		"""
		Check if there are more tokens.
		:return: True if we have more tokens in the input, false otherwise
		"""
		if self.__token_index >= len(self.__tokens):
			return self.__update_tokens()
		return True

	def advance(self):
		"""
		Gets the next token from the input and makes it the current token.
		This method should only be called if hasMoreTokens() is true.
		Initially there is no current token
		"""
		self.__token_index += 1

	def get_current_token(self):
		"""
		:return: The current token. Will raise an exception if there is no current token
		"""
		if self.__token_index >= len(self.__tokens):
			raise Exception(NO_TOKENS)
		return self.__tokens[self.__token_index]
