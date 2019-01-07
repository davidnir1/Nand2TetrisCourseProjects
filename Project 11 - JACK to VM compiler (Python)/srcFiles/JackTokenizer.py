# ============== Imports ==============

from srcFiles.TokenTypes import *
from srcFiles.Token import Token
import re

# ============= Constants =============

NO_TOKENS = 'Called get_current_token function while there are no tokens'
REGEX_PATTERN = r"[a-zA-Z0-9_]+|\".+?\"|\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~|\S+"
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
		input_file = open(input_file_path)
		self.__lines = self.__remove_comments(input_file.read())
		input_file.close()
		self.__tokens = []
		self.__token_index = 0
		self.__line_index = 0
		self.__parse_line()

	def __remove_comments(self, line):
		"""
		Receives a line with possible comments in it,
		and removes all allowed comments in jack language from the line.
		:param line: A line with possible comments in it
		:return: A line with no comments
		"""
		current_index = 0
		output = ''
		while current_index < len(line):
			if line[current_index] == "\"":
				string_end_index = line.find("\"", current_index + 1)
				output += line[current_index:string_end_index + 1]
				current_index = string_end_index + 1
			elif line[current_index] == "/":
				if line[current_index + 1] == "/":
					comment_end_index = line.find("\n", current_index + 1)
					current_index = comment_end_index + 1
					output += " "  # for the regex later
				elif line[current_index + 1] == "*":
					comment_end_index = line.find("*/", current_index + 1)
					current_index = comment_end_index + 2
					output += " "  # for the regex later
				else:
					output += line[current_index]
					current_index += 1
			else:
				output += line[current_index]
				current_index += 1
		return output

	def __parse_line(self):
		"""
		This function should be called only if all tokens in self.__tokens already been used
		It will clear this list and parse the next line from self.__input_file into that list.
		"""
		tokens = re.findall(REGEX_PATTERN, self.__lines)
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

	def has_more_tokens(self):
		"""
		Check if there are more tokens.
		:return: True if we have more tokens in the input, false otherwise
		"""
		return self.__token_index < len(self.__tokens)

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
